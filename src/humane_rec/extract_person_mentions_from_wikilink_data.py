#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : tmp.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Wed Jul 20 01:25:43 2016 (-0400)
| Last-Updated: Sun Sep  4 15:41:18 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 29
'''
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TFileObjectTransport
from bisect import bisect_left
import io
import sys
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--thrift_class_dir', default='data/wiki_link', type=str)
arg_parser.add_argument('--thrift_data_dir', default='data', type=str)
arg_parser.add_argument(
    '--out_fn', default='data/wiki_link_individual_mentions', type=str)
arg_parser.add_argument('--human_entity_fn', default=None, type=str)
args = arg_parser.parse_args()
sys.path.append(args.thrift_class_dir)
from edu.umass.cs.iesl.wikilink.expanded.data.constants import WikiLinkItem

pp = WikiLinkItem()
if args.human_entity_fn is not None:
    pool = set(['http://en.wikipedia.org/wiki/' + e.strip().split()[1]
                for e in open(args.human_entity_fn)])
else:
    from extract_person_mentions_from_wikilink_data_config import pool


import gzip
from collections import defaultdict
out_val = defaultdict(list)
for fn in xrange(1, 110):
    # with gzip.open(args.thrift_data_dir + '/%03d.gz' % fn) as f:
    with open(args.thrift_data_dir + '/%03d' % fn) as f:
        p = TBinaryProtocol.TBinaryProtocolAccelerated(
            TFileObjectTransport(f))
        print fn, len(out_val), sum(len(e) for e in out_val.itervalues())
        while True:
            try:
                pp.read(p)
            except EOFError:
                break
            for m in pp.mentions:
                c = m.context
                if c is not None:
                    url = m.wiki_url
                    if url in pool:
                        out_val[url].append([c.left, c.middle, c.right])

import cPickle as pickle
with open(args.out_fn, 'wb') as out_f:
    pickle.dump(dict(out_val), out_f, -1)
