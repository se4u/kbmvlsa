#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : tmp.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Wed Jul 20 01:25:43 2016 (-0400)
| Last-Updated: Sun Aug 28 23:29:10 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 35
'''
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TFileObjectTransport
import gzip
import sys
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--thrift_class_dir', default='data/wiki_link', type=str)
arg_parser.add_argument('--thrift_data_dir', default='/export/b15/prastog3/wikilinks', type=str)
arg_parser.add_argument(
    '--out_fn', default='data/wiki_link_url_counts.pkl', type=str)
args = arg_parser.parse_args()
sys.path.append(args.thrift_class_dir)
from edu.umass.cs.iesl.wikilink.expanded.data.constants import WikiLinkItem

pp = WikiLinkItem()


from collections import defaultdict
out_val = defaultdict(int)
for fn in xrange(1, 110):
    # with gzip.open(args.thrift_data_dir + '/%03d.gz' % fn) as f:
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
