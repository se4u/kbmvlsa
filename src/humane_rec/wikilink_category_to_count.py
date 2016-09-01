#!/usr/bin/env python
'''
| Filename    : wikilink_category_to_count.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Sep  1 12:34:31 2016 (-0400)
| Last-Updated: Thu Sep  1 12:55:13 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 4
'''
import cPickle as pkl
import rasengan
from wikilink_category_to_url_and_count_reverse_index import WikilinkReverseIndex
import sys
with rasengan.tictoc('loading pkl', override='stderr'):
    wri = pkl.load(open(sys.argv[1]))
for (a, b) in wri.iteritems():
    print '%s\t%d\t%d\t%s' % (
        a,
        len(b),
        sum([e[1] for e in b]),
        '\t'.join(str(e[1]) for e in b))
