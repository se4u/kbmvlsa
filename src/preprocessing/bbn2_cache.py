#!/usr/bin/env python
'''
| Filename    : bbn2_cache.py
| Description : Cache the intermediate files into pkl for faster loading.
| Author      : Pushpendre Rastogi
| Created     : Thu Apr 14 15:47:50 2016 (-0400)
| Last-Updated: Thu Apr 14 20:03:18 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 19
'''
import os
import sys
import rasengan
out_fn = sys.argv[1]
os.chdir(os.path.dirname(sys.argv[2]))
with rasengan.tictoc('Data Processing'):
    FOREIGN_NS = {}
    for row in ''' document    appearsInDocument
                   confidence  confidence_only
                   headquarter orgToHeadquarter
                   type        leaf_type
               '''.strip().split('\n'):
        ns, fn = row.strip().split()
        FOREIGN_NS[ns] = dict(row.strip().split() for row in open(fn))
    BASE_NS = {}
    for row in open('sort_base').read().strip().split('\n'):
        row = row.strip().split()
        if (row[0], row[1]) in BASE_NS:
            if row[1] == 'adept-core#person':
                tmp = BASE_NS[(row[0], row[1])]
                del BASE_NS[(row[0], row[1])]
                BASE_NS[row[0], '_a'] = tmp
                BASE_NS[row[0], '_b'] = ' '.join(row[2:])
            else:
                pass
        else:
            BASE_NS[(row[0], row[1])] = ' '.join(row[2:])

import cPickle as pkl

with open(out_fn, 'wb') as f:
    with rasengan.tictoc('Dumping pkl'):
        pkl.dump((FOREIGN_NS, BASE_NS), f, protocol=-1)

# import ujson
# with open(out_fn + '.json', 'wb') as f:
#     with rasengan.tictoc('Dumping ujson'):
#         ujson.dump([FOREIGN_NS, BASE_NS], f)
