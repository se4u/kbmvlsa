#!/usr/bin/env python
'''
| Filename    : catpeople_preprocessor_parses_to_pkl.py
| Description : Extract Parses to a faster loading pkl.
| Author      : Pushpendre Rastogi
| Created     : Sat Sep 24 15:50:21 2016 (-0400)
| Last-Updated: Sat Sep 24 18:54:30 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 15
'''
from util_catpeople import get_labelmap, proj_open, get_pfx, get_coarse_tagmap, get_fine_tagmap
import argparse, gzip
from shelve import DbfilenameShelf
import cPickle as pkl
from rasengan import groupby
PFX = get_pfx()
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--in_shelf', default=PFX + '/catpeople_clean_segmented_context.shelf', type=str)
arg_parser.add_argument('--parsefn', default=PFX + '/catpeople.parse.gz', type=str)
arg_parser.add_argument('--parse_pkl', default=PFX + '/catpeople.parse.pkl', type=str)
args=arg_parser.parse_args()
catpeople = DbfilenameShelf(args.in_shelf, protocol=-1, flag='r')
TM = catpeople['__TOKEN_MAPPER__']
labelmap = get_labelmap()
ctmap = get_coarse_tagmap()
ftmap =  get_fine_tagmap()
f = gzip.GzipFile(fileobj=proj_open(args.parsefn))
def get(e):
    e = e.split('\t')
    return [e[1], int(e[6]), e[7], e[3], e[4]]
PARSES={}
for parse in groupby(f):
    token, parent, labels, ctags, ftags = zip(*[get(r) for r in parse])
    token = tuple(TM(token))
    labels = labelmap(labels)
    ctags = ctmap(ctags)
    ftags = ftmap(ftags)
    PARSES[token] = [parent, labels, ctags, ftags]
print args.parse_pkl
pkl.dump(PARSES, open(args.parse_pkl, 'wb'), protocol=-1)
