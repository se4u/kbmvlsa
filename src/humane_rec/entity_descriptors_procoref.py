#!/usr/bin/env python
'''
| Filename    : entity_descriptors_procoref.py
| Description : Extract the descriptor tokens and store to a psv for easy readability.
| Author      : Pushpendre Rastogi
| Created     : Fri Aug  5 16:08:12 2016 (-0400)
| Last-Updated: Fri Aug 12 18:22:55 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 12
'''
import rasengan
from rasengan import sPickle
from rasengan.function_words import get_auxiliary_verbs
import sys
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('in_spkl_fn', type=str)
arg_parser.add_argument('--remove_auxiliary_verb', default=0, type=int)
args = arg_parser.parse_args()
if args.remove_auxiliary_verb:
    AUX_VERBS = set(get_auxiliary_verbs() + 'said'.split())

for (entity, mentions) in sPickle.s_load(open(args.in_spkl_fn)):
    t_pool = []
    for m in mentions:
        for s in m['sentences']:
            d = s['d']
            if len(d):
                t = [_.strip().split('\t')[1] for _ in s['p']]
                t_pool += [t[e] for e in d]
    if args.remove_auxiliary_verb:
        t_pool = [e for e in t_pool if e.lower() not in AUX_VERBS]

    print entity, '|||', ' '.join(
        '%s:%d' % (a, b) for a, b in rasengan.uniq_c(t_pool, sort=True))
