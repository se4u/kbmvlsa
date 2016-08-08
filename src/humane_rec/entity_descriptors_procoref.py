#!/usr/bin/env python
'''
| Filename    : entity_descriptors_procoref.py
| Description : Extract the descriptor tokens and store to a psv for easy readability.
| Author      : Pushpendre Rastogi
| Created     : Fri Aug  5 16:08:12 2016 (-0400)
| Last-Updated: Fri Aug  5 16:25:15 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 5
'''
import rasengan
from rasengan import sPickle
import sys

for (entity, mentions) in sPickle.s_load(open(sys.argv[1])):
    t_pool = []
    for m in mentions:
        for s in m['sentences']:
            d = s['d']
            if len(d):
                t = [_.strip().split('\t')[1] for _ in s['p']]
                t_pool += [t[e] for e in d]
    print entity, '|||', ' '.join(
        '%s:%d' % (a, b) for a, b in rasengan.uniq_c(t_pool, sort=True))
