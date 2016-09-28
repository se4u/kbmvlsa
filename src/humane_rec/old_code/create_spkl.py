#!/usr/bin/env python
'''
| Filename    : wikimic_create_entity_token_set.ipkl.py
| Description : Convert a giant pickle file that can't be processed
|               conveniently with other data into a streaming pkl.
| Author      : Pushpendre Rastogi
| Created     : Fri Aug  5 11:37:23 2016 (-0400)
| Last-Updated: Fri Aug  5 11:47:29 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 1
'''
import argparse
from rasengan import sPickle, tictoc
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--in_fn', type=str)
arg_parser.add_argument('--out_fn', type=str)
args = arg_parser.parse_args()
with tictoc('Loading Data'):
    import cPickle as pkl
    data = pkl.load(open(args.in_fn))
with tictoc('Writing Data'):
    with open(args.out_fn, 'wb') as f:
        sPickle.s_dump(data.iteritems(), f)
