#!/usr/bin/env python
'''
| Filename    : cat-people-dev.split.py
| Description : For each (category, fold) write the train and test.
| Author      : Pushpendre Rastogi
| Created     : Sun Sep  4 17:48:42 2016 (-0400)
| Last-Updated: Sun Sep  4 18:11:38 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 20
'''
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--seed', default=1234, type=int, help='Default={0}')
arg_parser.add_argument('--fold', default=3, type=int)
arg_parser.add_argument('--in_fn', default='data/cat-people-dev', type=str)
arg_parser.add_argument(
    '--out_fn', default='data/cat-people-dev.fold.pkl', type=str)
args = arg_parser.parse_args()
import random
random.seed(args.seed)
from rasengan import groupby
from collections import defaultdict
import cPickle as pkl


def split_list(l, i, j):
    return ((l[:i] + l[j:]), l[i:j])

d = defaultdict(list)
for cat in groupby(args.in_fn, predicate=lambda x: x.split()[0]):
    L = range(len(cat))
    random.shuffle(L)
    len_test = len(L) / args.fold
    d[cat[0].split()[0]] = [split_list(L, test_begin, test_begin + len_test)
                            for test_begin
                            in (range(0, args.fold * len_test, len_test))]
with open(args.out_fn, 'w') as f:
    pkl.dump(dict(d), f)
