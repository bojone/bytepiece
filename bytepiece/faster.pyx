# cython: language_level=3
from libc.time cimport time
from libc.stdlib cimport RAND_MAX, rand, srand
from libc.math cimport INFINITY, exp, log

srand(time(NULL))


cdef inline double random():
    return rand() / float(RAND_MAX)


cdef inline double logsumexp(double x, double y):
    if x < y:
        x, y = y, x
    return x + log(1 + exp(y - x))


def _tokenize(self, bytes text, double alpha=-1):
    cdef int e, k, s
    cdef double v, score
    cdef list scores = [0] + [-INFINITY] * len(text)
    cdef list routes = list(range(len(text) + 1))
    cdef list tokens = []
    for e, (k, v) in self._automaton.iter(text):
        s, e = e - k + 1, e + 1
        if alpha < 0:
            score = scores[s] + v
            if score > scores[e]:
                scores[e], routes[e] = score, s
        else:
            score = scores[s] + alpha * v
            scores[e] = logsumexp(scores[e], score)
            if random() < exp(score - scores[e]):
                routes[e] = s
    while text:
        s = routes[e]
        tokens.append(text[s:e])
        text, e = text[:s], s
    return tokens[::-1]