#!/usr/bin/env python
'''
| Filename    : util_catpeople.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Sep 19 01:51:46 2016 (-0400)
| Last-Updated: Mon Sep 19 02:06:58 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 3
'''
from rasengan.function_words import get_function_words
import catpeople_baseline_nb_config


def get(l, idi):
    return [l[i] for i in idi]


def minus(E, S):
    S = set(S)
    return [e for e in E if e not in S]


def remove_unigrams(w, tmo):
    bad_idx = []
    for e in get_function_words():
        e = e.lower()
        try:
            idx = tmo([e])[0]
            del w[idx]
            bad_idx.append(idx)
        except KeyError:
            continue
    return w, bad_idx


def remove_bigrams(w, bad_idx):
    for index in w.keys():
        ct = index % catpeople_baseline_nb_config.MAX_TOK
        pt = ((index - ct) / catpeople_baseline_nb_config.MAX_TOK - 1)
        if pt in bad_idx or ct in bad_idx:
            del w[index]
    return w


def color(f):
    assert 0 <= f <= 1
    return tuple([int(f * 7) * 32] * 3)
