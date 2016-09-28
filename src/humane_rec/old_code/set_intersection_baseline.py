#!/usr/bin/env python
'''
| Filename    : set_intersection_baseline.py
| Description : Implement a set intersection baseline.
| Author      : Pushpendre Rastogi
| Created     : Sat Aug  6 15:02:04 2016 (-0400)
| Last-Updated: Sat Aug  6 15:30:19 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
from collections import defaultdict as d
dd = d(int)
for row in (e for e in open('data/tmp.psv') if e != '\n'):
    e, row = row.strip().split(' ||| ')
    for tags in (_.strip().split(':')[0] for _ in row.strip().split()):
        dd[tags] += 1

print '\n'.join('%-20s %d' % (a, b) for a, b in sorted(dd.items(), key=lambda x: x[1], reverse=True))
