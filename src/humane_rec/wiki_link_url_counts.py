#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : wiki_link_url_counts.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Wed Jul 20 01:25:43 2016 (-0400)
| Last-Updated: Wed Sep  7 11:13:01 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 37
'''
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TFileObjectTransport
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--thrift_class_dir', default='data/wiki_link', type=str)
arg_parser.add_argument('--thrift_data_dir', default='/export/b15/prastog3/wikilinks', type=str)
arg_parser.add_argument(
    '--out_fn', default='data/wiki_link_url_counts.pkl', type=str)
args = arg_parser.parse_args()
import sys
sys.path.append(args.thrift_class_dir)
from edu.umass.cs.iesl.wikilink.expanded.data.constants import WikiLinkItem

pp = WikiLinkItem()

from collections import defaultdict
out_val = defaultdict(int)

for fn in xrange(1, 110):
    with open(args.thrift_data_dir + '/%03d' % fn) as f:
        p = TBinaryProtocol.TBinaryProtocolAccelerated(
            TFileObjectTransport(f))
        print fn, len(out_val)
        while True:
            try:
                pp.read(p)
            except EOFError:
                break
            for m in pp.mentions:
                c = m.context
                if c is not None:
                    url = m.wiki_url
                    out_val[url] += 1


import cPickle as pickle
with open(args.out_fn, 'wb') as  out_f:
    pickle.dump(dict(out_val), out_f, -1)
