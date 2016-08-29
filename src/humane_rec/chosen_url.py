#!/usr/bin/env python
'''
| Filename    : chose_url.py
| Description : Print the chosen urls into a single file based on chosen categories.
| Author      : Pushpendre Rastogi
| Created     : Mon Aug 29 18:35:44 2016 (-0400)
| Last-Updated: Mon Aug 29 18:42:06 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 3
'''
import cPickle as pkl
from wikilink_category_to_url_and_count_reverse_index import WikilinkReverseIndex
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--caturl_pkl', default='data/wikilink_category_to_url_and_count_reverse_index.pkl', type=str)
arg_parser.add_argument(
    '--chosen_cat', default='data/chosen_wikilink_categories', type=str)
args = arg_parser.parse_args()
chosen_cat = set([e.strip().split()[0] for e in open(args.chosen_cat)])
caturl = pkl.load(open(args.caturl_pkl))
for cat in chosen_cat:
    for url, _ in caturl[cat]:
        print cat, url
