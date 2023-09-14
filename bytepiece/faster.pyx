# cython: language_level=3
from libc.time cimport time
from libc.stdlib cimport RAND_MAX, rand, srand
from libc.math cimport INFINITY, exp

srand(time(NULL))


cdef inline double random():
    return rand() / float(RAND_MAX)


cdef inline double sigmoid(double x):
    if x >= 0:
        return 1. / (1. + exp(-x))
    else:
        return 1. - 1. / (1. + exp(x))


def _tokenize(self, bytes text, double alpha=-1):
    cdef int e, k, s
    cdef double v, score
    cdef list scores = [0] + [-INFINITY] * len(text)
    cdef list routes = list(range(len(text) + 1))
    cdef list tokens = []
    for e, (k, v) in self._automaton.iter(text):
        s, e = e - k + 1, e + 1
        score = scores[s] + v
        if alpha <= 0 and score > scores[e]:
            scores[e], routes[e] = score, s
        elif alpha > 0 and random() < sigmoid((score - scores[e]) * alpha):
            scores[e], routes[e] = score, s
    while text:
        s = routes[e]
        tokens.append(text[s:e])
        text, e = text[:s], s
    return tokens[::-1]
