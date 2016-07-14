#!/usr/bin/env python
'''
| Filename    : analyze_categories_of_individuals.txt.py
| Description : Analyze the categories of individuals.
| Author      : Pushpendre Rastogi
| Created     : Thu Jul 14 15:20:41 2016 (-0400)
| Last-Updated: Thu Jul 14 15:49:03 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 21
'''
import argparse
from collections import defaultdict
import rasengan

arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--d1', default=' |||', type=str)
arg_parser.add_argument('--d2', default=';', type=str)
arg_parser.add_argument('--cat_col', default=10, type=int)
arg_parser.add_argument(
    '--in_fn', default='data/mention_and_type_for_individuals', type=str)
arg_parser.add_argument('--link_col', default=8, type=int)
arg_parser.add_argument('--link_count_thresh', default=5, type=int)
arg_parser.add_argument('--link_to_count_fn',
                        default='data/counts_of_mentions_of_individuals.txt',
                        type=str)
args = arg_parser.parse_args()
d = defaultdict(dict)


def process(t):
    return (t[1], int(t[0]))
link_to_count = dict([process(e.strip().split())
                      for e
                      in open(args.link_to_count_fn, encoding='utf-8')])
with rasengan.debug_support():
    with open(args.in_fn, encoding='utf-8') as f:
        for line in f:
            line = line.strip().split(args.d1)
            links = line[args.link_col].strip().split()
            cat_col = line[args.cat_col]
            cats = cat_col.strip().split(args.d2)
            for link in links:
                if link in link_to_count and link_to_count[link] >= args.link_count_thresh:
                    for cat in cats:
                        d[cat.strip()][link] = 1
d = dict(d)
for (cat, entities) in sorted(d.items(), key=lambda x: len(x[1]), reverse=True):
    print(cat, len(entities))  # , list(entities)
