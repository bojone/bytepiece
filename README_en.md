[[中文](https://github.com/bojone/bytepiece/blob/main/README.md)|English]

# BytePiece
BytePiece is a Byte-based Unigram tokenizer, implemented purely in Python, making it more readable and expandable. Due to the use of a new training algorithm, its compression rate is often higher than existing Tokenizers, and it also supports multiprocessing acceleration for training. Moreover, it directly operates on the UTF-8 Bytes of the text, with almost no preprocessing, making it more pure and language-independent.

Blog: 
- https://kexue.fm/archives/9752
- https://kexue.fm/archives/9768

## Characteristics

An ideal Tokenizer and its training algorithm should have the following characteristics:
- Lossless reconstruction
- High compression rate
- Language-independent
- Data-driven
- Training-friendly

The mainstream [SentencePiece](https://github.com/google/sentencepiece) basically has the above characteristics, but there are still some problems. For example, it supports both BPE and Unigram algorithms. BPE often has a higher compression rate, but the training is extremely slow and consumes a lot of memory. Moreover, it does conduct some language-related preprocessing on the text, so it's not purely "language-independent". Besides, it's written in C++, which is a black box for most users, thus not conducive to research and modification.

BytePiece has conceived a new training method based on **Byte-based N-gram Language Model (BNLM)** , which can obtain a higher compression rate vocabulary table, support multiprocessing training, and significantly accelerate compared to SentencePiece's BPE training under the same corpus. The code is pure Python, easy for everyone to read and modify. In addition, BytePiece also provides a more efficient random segmentation algorithm than [Subword Regularization](https://arxiv.org/abs/1804.10959).

## Principle

BytePiece is not simply a rewrite of the existing Unigram model based on Byte-based and multiprocessor, but a new training method designed for Unigram, which is one of the key reasons for its higher compression rate.

The new training method is based on the new word discovery algorithm of the N-gram language model, first proposed in the author's blog 7 years ago [《【Chinese Word Segmentation Series】 5. Unsupervised Word Segmentation Based on Language Model》](https://kexue.fm/archives/3956). Please visit the blog for details.

For the new random segmentation algorithm, you can refer to ["A Brief Exploration of Random Segmentation: From Viterbi Decoding to Viterbi Sampling"](https://kexue.fm/archives/9768) and ["Further Exploration of Random Segmentation: From Viterbi Sampling to Perfect Sampling Algorithm"](https://kexue.fm/archives/9811).

## Installation

BytePiece can only run on Python3 and uses [pyahocorasick](https://github.com/WojciechMula/pyahocorasick) to accelerate the training process. Since BytePiece is Byte-based, and the pyahocorasick on PyPi is Unicode-based, it cannot be used directly. Please follow the instructions below to install the Byte-based version of pyahocorasick:
```bash
# If already installed, please uninstall first
pip uninstall pyahocorasick

# Compile and install directly from git, note to pass the environment variable AHOCORASICK_BYTES
AHOCORASICK_BYTES=1 pip install git+https://github.com/WojciechMula/pyahocorasick.git
```
Then install Cython:
```bash
pip install Cython
```
After that, you can install BytePiece via pip:
```bash
pip install bytepiece==0.6.1
```

## Usage

All source code of BytePiece is actually in a single file, including `Trainer` and `Tokenizer` two classes, corresponding to training and tokenization respectively.

### Training

To train Tokenizer, you just need to import the `Trainer` class:
```python
from bytepiece import Trainer
```
Then prepare the training corpus. BytePiece supports not reading all corpora into memory at once, but since BytePiece training needs to go through the data twice, it does not support Generator input, but needs to be written in the form of Iterator, for example:
```python
import json

class corpus:
    def __iter__(self):
        f = 'data_sample.json'
        with open(f) as f:
            for l in f:
                yield json.loads(l)['text']  # Return a Unicode each time
```
Then you can start the actual training:
```python
trainer = Trainer(order=6, max_vocab_size=100000, min_count=32)
trainer.train(corpus(), workers=64, batch_size=1000)
trainer.save('bytepiece.model')
```
Here, `order` is the order of the n-gram language model, it is recommended to keep the default `order=6`; `max_vocab_size` is the maximum size of the vocabulary, note that due to redundancy removal, the final vocabulary may not precisely equal max_vocab_size, it might be slightly less; `min_count` is the minimum occurrence frequency of tokens, when the data volume is large, it can be appropriately increased, it generally doesn't significantly affect the training results; `workers` is the number of parallel training processes, which can utilize all cores of the machine; `batch_size` is the batch size, it won't affect the training results, it usually doesn't need to be changed, if you find the CPU utilization is not full, you can appropriately increase it.

In addition, starting from version `0.4.1`, a new parameter `isolate_digits` is added, which defaults to `False`. When set to `True`, it ensures that all Arabic numbers are split into individual characters:
```python
trainer = Trainer(order=6, max_vocab_size=100000, min_count=32, isolate_digits=True)
```
Starting from version `0.6.0`, a new parameter `ensure_unicode` is added, which can ensure that all multi-byte tokens can be restored to unicode. Since the current results show that enabling `ensure_unicode` often results in a higher compression rate for the trained model, it is set to `True` by default. When set to `False` (equivalent to versions before 0.6.0), multi-byte tokens may need `decode(errors='ignore')` to be restored to unicode:
```python
trainer = Trainer(order=6, max_vocab_size=100000, min_count=32, ensure_unicode=True)
```

### Tokenization

After the training is completed, refer to the following usage:
```python
from bytepiece import Tokenizer

tokenizer = Tokenizer('bytepiece.model')
text = 'Today's weather is great'

tokens = tokenizer.tokenize(text)  # Returns a list of bytes
print(b' '.join(tokens).decode(errors='ignore'))  # Visualize the tokenization result

ids = tokenizer.encode(text)  # Returns the ids corresponding to tokens
print(tokenizer.decode(ids))  # Decode the ids back to unicode text

tokens = tokenizer.tokenize(text, alpha=0.2)  # Random Tokenization
print(b' '.join(tokens).decode(errors='ignore'))  # Visualize the tokenization result
```

## Comparison

Comparison with small data volume:

|  | Training Time↓ | Maximum Memory Usage↓ | Compression Rate↑ | Tokenization Speed↑ |
| :----: | :----: | :----: | :----: | :----: |
| SP-BPE | 55.3 minutes | 5.2GB | 4.80 | 5.47 |
| SP-Unigram | 1.6 minutes | 2.5GB | 4.73 | 7.84 |
| BytePiece | 6.5 minutes | 4.3GB | 5.05 | 2.50 |

Comparison with large data volume:

|  | Training Time↓ | Maximum Memory Usage↓ | Compression Rate (Homologous)↑ | Compression Rate (Heterologous)↑ | Tokenization Speed↑ |
| :----: | :----: | :----: | :----: | :----: | :----: |
| SP-BPE | 19.21 hours | 97GB | 4.52 | 4.46 | 1.27 |
| SP-Unigram | 2.02 hours | 384GB | 4.51 | 4.48 | 5.55 |
| BytePiece | 2.24 hours | 51GB | 5.39 | 4.51 | 1.92 |

The unit of compression rate is "bytes/token", i.e., the average number of bytes per token; the unit of speed is "M bytes/second", i.e., the average number of bytes that can be segmented per second (in millions). For other details, please refer to [here](https://kexue.fm/archives/9752#%E6%95%88%E6%9E%9C%E6%B5%8B%E8%AF%95).

In the first table, the dataset has a shorter average length, BytePiece is slower than both SP-BPE and SP-Unigram; in the second table, the average length of the corpus is generally longer, resulting in BytePiece being faster than SP-BPE. This indicates that BPE's tokenization speed is significantly affected by length, and also indicates that BytePiece's tokenization speed, accelerated by Cython, can be compared with SentencePiece in terms of speed.

## Download

To download the open-source BytePiece model, please go to [models](https://github.com/bojone/bytepiece/tree/main/models).

## Citation

```
@misc{bytepiece2023,
  title={BytePiece: A more pure and effective tokenizer},
  author={Jianlin Su},
  year={2023},
  howpublished={\url{https://github.com/bojone/bytepiece}},
}
```

## Communication
QQ Group: 67729435, for WeChat group please add robot spaces_ac_cn
