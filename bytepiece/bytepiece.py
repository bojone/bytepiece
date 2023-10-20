# -*- coding: utf-8 -*-
# Reference 1: https://kexue.fm/archives/9752
# Reference 2: https://kexue.fm/archives/9768

import numpy as np
import re, json, unicodedata
from itertools import chain
from functools import partial
from tqdm import tqdm, trange
from base64 import b64encode, b64decode
from multiprocessing import Pool, Queue
import ahocorasick
from . import faster


def normalize(text, maxlen=0, isolate_digits=False):
    text = unicodedata.normalize('NFC', text)
    if maxlen > 0:
        if isolate_digits:
            regex = '\d|[^\n\d]{,%d}\n{1,100}|[^\n\d]{1,%d}' % (maxlen, maxlen)
        else:
            regex = '.{,%d}\n{1,100}|.{1,%d}' % (maxlen, maxlen)
    else:
        if isolate_digits:
            regex = '\d|[^\n\d]*\n+|[^\n\d]+'
        else:
            regex = '.*\n+|.+'
    return [t.encode() for t in re.findall(regex, text)]


class Trainer:
    """A novel unsupervised training algorithm for Unigram
    Reference: https://kexue.fm/archives/3956
    """
    def __init__(
        self,
        order=6,
        max_vocab_size=10000,
        max_piece_length=36,
        min_count=2,
        isolate_digits=False,
        ensure_unicode=True
    ):
        self.order = order
        self.max_piece_length = max_piece_length
        self.min_count = min_count
        self.isolate_digits = isolate_digits
        self.ensure_unicode = ensure_unicode
        if isinstance(max_vocab_size, list):
            self.max_vocab_size = sorted(max_vocab_size)[::-1]
        else:
            self.max_vocab_size = [max_vocab_size]

    def count_ngrams(self, texts):
        ngrams = [{} for i in range(self.order + 1)]
        for text in texts:
            for i in range(len(text)):
                for j in range(self.order + 1):
                    k = text[i:i + j]
                    ngrams[j][k] = ngrams[j].get(k, 0) + 1
        return ngrams

    def prune_ngrams(self, ngrams):
        for i in range(256):
            if bytes([i]) not in ngrams[1]:
                ngrams[1][bytes([i])] = 1
                ngrams[0][b''] += 1
        for i in trange(len(ngrams) - 1, -1, -1, desc='Prune Ngrams', ncols=0):
            ngrams[i] = {
                k: np.log(v)
                for k, v in ngrams[i].items()
                if len(k) == i and v >= (self.min_count if i > 1 else 0)
            }
            if i < len(ngrams) - 1:
                ngrams[i + 1] = {
                    k: v - ngrams[i][k[:i]]
                    for k, v in ngrams[i + 1].items()
                }
        return ngrams

    @property
    def trans(self):
        if not hasattr(self, '_trans'):
            self._trans = np.full((self.order, self.order), -np.inf)
            for i in range(self.order):
                self._trans[i, 0] = 0
                self._trans[i, min(i + 1, self.order - 1)] = 0
        return self._trans

    def _tokenize(self, text):
        # Nodes
        nodes = np.full((len(text), self.order), -np.inf)
        for j in range(self.order):
            for i in range(j, len(text)):
                nodes[i, j] = self.ngrams[j + 1].get(text[i - j:i + 1], -np.inf)
        if self.ensure_unicode:
            text_array = np.frombuffer(text, dtype=np.uint8)
            nodes[(text_array >= 128) & (text_array < 192), 0] -= np.inf
        # Viterbi
        routes = np.zeros((len(text) - 1, self.order), dtype='int32')
        for i in range(1, len(nodes)):
            scores = nodes[i - 1][:, None] + self.trans + nodes[i]
            routes[i - 1] = scores.argmax(0)
            nodes[i] = scores.max(0)
        # Output
        opt_route = [nodes[-1].argmax()]
        for i in range(1, len(nodes)):
            opt_route.append(routes[-i][opt_route[-1]])
        opt_route = np.array(opt_route[::-1])
        opt_route = np.append(np.where(opt_route == 0)[0], len(nodes))
        return [text[s:e] for s, e in zip(opt_route, opt_route[1:])]

    def count_pieces(self, texts):
        pieces = {}
        for text in texts:
            for p in self._tokenize(text):
                pieces[p] = pieces.get(p, 0) + 1
        return pieces

    def split_pieces(self, keep, drop):
        tokenizer, counter = Tokenizer(self.dump(keep)), {}
        for k, v in drop:
            for p in tokenizer._tokenize(k):
                counter[p] = counter.get(p, 0) + v
        return counter

    def prune_pieces(self, pieces, workers=1, batch_size=1000):
        desc = 'Prune Pieces'
        split_pieces = partial(
            self.psplit_pieces, workers=workers, batch_size=batch_size
        ) if workers > 1 else self.split_pieces
        # Complete all bytes
        for i in range(256):
            if bytes([i]) not in pieces:
                pieces[bytes([i])] = 1
        # Prune by frequency and length
        keep_pieces, drop_pieces = {}, {}
        for k, v in pieces.items():
            if len(k) == 1 or (
                len(k) <= self.max_piece_length and v >= self.min_count
            ):
                keep_pieces[k] = v
            else:
                drop_pieces[k] = v
        drop_pieces = tqdm(drop_pieces.items(), desc=desc, ncols=0)
        for k, v in split_pieces(keep_pieces, drop_pieces).items():
            keep_pieces[k] += v
        # Prune wasted pieces
        while True:
            len_keep_pieces = len(keep_pieces)
            drop_pieces = tqdm(keep_pieces.items(), desc=desc, ncols=0)
            keep_pieces = split_pieces(keep_pieces, drop_pieces)
            if len_keep_pieces == len(keep_pieces):
                break
        # Prune by max_vocab_size
        final_pieces = []
        for max_vocab_size in self.max_vocab_size:
            if len(keep_pieces) <= max_vocab_size - 3:
                final_pieces.append(keep_pieces)
                continue
            pieces = sorted(
                keep_pieces.items(),
                key=lambda t: (len(t[0]) > 1, -t[1], -len(t[0]), t[0])
            )
            keep_pieces = dict(pieces[:max_vocab_size - 3])
            drop_pieces = tqdm(pieces[max_vocab_size - 3:], desc=desc, ncols=0)
            for k, v in split_pieces(keep_pieces, drop_pieces).items():
                keep_pieces[k] += v
            # Prune wasted pieces
            while True:
                len_keep_pieces = len(keep_pieces)
                drop_pieces = tqdm(keep_pieces.items(), desc=desc, ncols=0)
                keep_pieces = split_pieces(keep_pieces, drop_pieces)
                if len_keep_pieces == len(keep_pieces):
                    break
            final_pieces.append(keep_pieces)
        # Output
        return final_pieces

    def norm(self, texts):
        for text in texts:
            for t in normalize(text, 10000, self.isolate_digits):
                yield t

    def train(self, texts, workers=1, batch_size=1000):
        if workers > 1:
            texts1 = self.norm(tqdm(texts, desc='Count Ngrams'))
            self.ngrams = self.pcount_ngrams(texts1, workers, batch_size)
            self.ngrams = self.prune_ngrams(self.ngrams)
            texts2 = self.norm(tqdm(texts, desc='Count Pieces'))
            self.pieces = self.pcount_pieces(texts2, workers, batch_size)
            self.pieces = self.prune_pieces(self.pieces, workers, batch_size)
        else:
            texts1 = self.norm(tqdm(texts, desc='Count Ngrams'))
            self.ngrams = self.count_ngrams(texts1)
            self.ngrams = self.prune_ngrams(self.ngrams)
            texts2 = self.norm(tqdm(texts, desc='Count Pieces'))
            self.pieces = self.count_pieces(texts2)
            self.pieces = self.prune_pieces(self.pieces)

    def dump(self, pieces):
        pieces = sorted(pieces.items(), key=lambda t: (len(t[0]), t[0]))
        return {
            b64encode(k).decode(): [i + 3, k.decode(errors='ignore'), v]
            for i, (k, v) in enumerate(pieces)
        }

    def save(self, path):
        if len(self.pieces) == 1:
            paths = [path]
        else:
            paths = ['%s.%s' % (path, size) for size in self.max_vocab_size]
        for pieces, path in zip(self.pieces, paths):
            json.dump(
                self.dump(pieces),
                open(path, 'w'),
                indent=4,
                ensure_ascii=False
            )

    def pcount(self, inputs, count, merge, init, desc, workers, batch_size):
        def worker_func(in_queue, out_queue):
            counter = init()
            while True:
                inputs = in_queue.get()
                if inputs is None:
                    break
                merge(counter, count(inputs))
            out_queue.put(counter)

        # Count
        in_queue, out_queue = Queue(workers + 1), Queue()
        pool = Pool(workers, worker_func, (in_queue, out_queue))
        batch = []
        for input in inputs:
            batch.append(input)
            if len(batch) == batch_size:
                in_queue.put(batch)
                batch = []
        if batch:
            in_queue.put(batch)
        for i in range(workers):
            in_queue.put(None)
        # Merge
        counter = init()
        for _ in trange(workers, desc=desc, ncols=0):
            merge(counter, out_queue.get())
        pool.terminate()
        return counter

    def pcount_ngrams(self, texts, workers=1, batch_size=1000):
        def merge(ngrams1, ngrams2):
            for i, G in enumerate(ngrams2):
                for k, v in G.items():
                    ngrams1[i][k] = ngrams1[i].get(k, 0) + v

        init = lambda: [{} for i in range(self.order + 1)]
        return self.pcount(
            texts, self.count_ngrams, merge, init, 'Merge Ngrams', workers,
            batch_size
        )

    def psplit_pieces(self, keep, drop, workers=1, batch_size=1000):
        def merge(pieces1, pieces2):
            for k, v in pieces2.items():
                pieces1[k] = pieces1.get(k, 0) + v

        split_pieces = lambda drop: self.split_pieces(keep, drop)
        return self.pcount(
            drop, split_pieces, merge, dict, 'Merge Pieces', workers,
            batch_size * 10
        )

    def pcount_pieces(self, texts, workers=1, batch_size=1000):
        def merge(pieces1, pieces2):
            for k, v in pieces2.items():
                pieces1[k] = pieces1.get(k, 0) + v

        return self.pcount(
            texts, self.count_pieces, merge, dict, 'Merge Pieces', workers,
            batch_size // 10
        )


class Tokenizer:
    """Unigram tokenizer with Aho-Corasick automaton
    """
    def __init__(self, pieces):
        if isinstance(pieces, str):
            pieces = json.load(open(pieces))
        pieces = {b64decode(k): v for k, v in pieces.items()}
        self._pieces = {k: v[-1] for k, v in pieces.items()}
        self._piece2id = {k: v[0] for k, v in pieces.items()}
        for i, k in enumerate(['<pad>', '<bos>', '<eos>']):
            self._piece2id[k] = i
        self._id2piece = {v: k for k, v in self._piece2id.items()}
        self.vocab_size = len(self._pieces) + 3
        # Aho-Corasick automaton
        log_total = np.log(sum(self._pieces.values()))
        self._automaton = ahocorasick.Automaton()
        for k, v in self._pieces.items():
            self._automaton.add_word(k, (len(k), np.log(v) - log_total))
        self._automaton.make_automaton()

    def _tokenize(self, text, alpha=-1):
        return faster._tokenize(self, text, alpha)

    def tokenize(self, text, alpha=-1):
        return list(chain(*[self._tokenize(t, alpha) for t in normalize(text)]))

    def piece_to_id(self, p):
        return self._piece2id[p]

    def id_to_piece(self, i):
        return self._id2piece[i]

    def pieces_to_ids(self, pieces):
        return [self._piece2id[p] for p in pieces]

    def ids_to_pieces(self, ids):
        return [self._id2piece[i] for i in ids]

    def encode(self, text, add_bos=False, add_eos=False, alpha=-1):
        pieces = [self._piece2id[p] for p in self.tokenize(text, alpha)]
        if add_bos:
            pieces = [1] + pieces
        if add_eos:
            pieces += [2]
        return pieces

    def decode(self, ids):
        pieces = [self._id2piece[i] for i in ids if i > 2]
        return b''.join(pieces).decode(errors='ignore')
