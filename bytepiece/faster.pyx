# cython: language_level=3
from libc.math cimport INFINITY


def _tokenize(bytes text, dag):
    cdef int e, k, s
    cdef float v, score
    cdef list routes = [(0, None)] + [(-INFINITY, None) for _ in text]
    cdef list tokens = []
    for e, (k, v) in dag:
        s, e = e - k + 1, e + 1
        score = routes[s][0] + v
        if score > routes[e][0]:
            routes[e] = score, s
    while text:
        s = routes[e][1]
        tokens.append(text[s:e])
        text, e = text[:s], s
    return tokens[::-1]
