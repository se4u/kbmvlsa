#!/usr/bin/env python
'''
| Filename    : wikilink_category_to_count.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Sep  1 12:34:31 2016 (-0400)
| Last-Updated: Thu Sep  1 13:05:00 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 7
'''
import cPickle as pkl
import rasengan
from wikilink_category_to_url_and_count_reverse_index import WikilinkReverseIndex
import sys
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--in_pkl_fn', default='data/wikilink_category_to_url_and_count_reverse_index.pkl', type=str)
arg_parser.add_argument('--out_fn', default='data/wikilink_category_to_count.tsv', type=str)
arg_parser.add_argument('--mention_thresh', default=10, type=int)
arg_parser.add_argument('--count_total_url', default=0, type=int)
arg_parser.add_argument('--count_url', default=0, type=int)
args=arg_parser.parse_args()
with rasengan.tictoc('loading pkl', override='stderr'):
    wri = pkl.load(open(args.in_pkl_fn))

total_url = {}
def update_total_url(b):
    for e,c in b:
        if e not in total_url:
            total_url[e] = c
        else:
            assert total_url[e] == c, str((e, c))
    return

with open(args.out_fn, 'wb') as f:
    for (a, b) in wri.iteritems():
        if args.count_total_url:
            update_total_url(b)
        else:
            b = [e for e in b if e[1] >= args.mention_thresh]
            if args.count_url:
                update_total_url(b)
            else:
                f.write('%s\t%d\t%d\t%s\n' % (
                    a, len(b), sum([e[1] for e in b]), ' '.join(str(e[1]) for e in b)))
if args.count_total_url or args.count_url:
    print len(total_url), sum(total_url.itervalues())
