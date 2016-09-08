#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : catpeople_wikilink_mentions.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Wed Jul 20 01:25:43 2016 (-0400)
| Last-Updated: Wed Sep  7 19:54:10 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 90
'''
from thrift.protocol import TBinaryProtocol
from thrift.transport.TTransport import TFileObjectTransport
import os
import bz2
import rasengan
from collections import defaultdict
from util_wikiurl import get_redirect, simplify_wiki_url
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--thrift_class_dir', default='data/wiki_link', type=str)
arg_parser.add_argument('--human_entity_fn', default='data/cat-people', type=str,
                        choices=['data/cat-people', 'ace2005_pilot'])
PDIR = ('/export/b15/prastog3/' if os.uname()[1] == 'b15' else 'data/')
arg_parser.add_argument('--thrift_data_dir', default='%s/wikilinks'%PDIR, type=str)
arg_parser.add_argument('--out_fn',
                        default='%s/catpeople_wikilink_mentions.shelf'%PDIR, type=str)
arg_parser.add_argument('--last_f2r', default=110, type=int)
args = arg_parser.parse_args()
import sys
sys.path.append(args.thrift_class_dir)
from edu.umass.cs.iesl.wikilink.expanded.data.constants import WikiLinkItem

# ----------------------------- #
# Create a pool of urls to keep #
# ----------------------------- #
if args.human_entity_fn == 'data/cat-people':
    POOL = set([e.strip().split()[1]
                for e in open(args.human_entity_fn)])
elif args.human_entity_fn == 'ace2005_pilot':
    from ace_2005_pilot_pool import POOL
else:
    raise NotImplementedError

# ----------------------------- #
# Load the map of url redirects #
# ----------------------------- #
with rasengan.tictoc('Loading Redirects'): # 36s
    redirect = get_redirect()

def get_mention_from_wikilink_thrift_file(fn):
    f = open(args.thrift_data_dir + '/%03d' % fn)
    out_val = defaultdict(list)
    p = TBinaryProtocol.TBinaryProtocolAccelerated(
        TFileObjectTransport(f))
    pp = WikiLinkItem()
    while True:
        try:
            pp.read(p)
        except EOFError:
            break
        for m in pp.mentions:
            c = m.context
            if c is not None:
                url = simplify_wiki_url(m.wiki_url)
                # Follow url redirect.
                try:
                    url = redirect[hash(url)]
                except KeyError:
                    pass
                if url in POOL:
                    # if c.left.startswith('the Musical August 30th, 2009 | Author: operator Shrek the Musical is a musical with music by Jeanine Tesori and a book and lyrics'):
                    #     print 1, fn
                    out_val[url].append([c.left, c.middle, c.right])
    print fn, len(out_val), sum(len(e) for e in out_val.itervalues())
    out_val.default_factory = None # FINALIZE out_val
    return out_val


with rasengan.tictoc('Reading wikilinks'):
    # With joblib this takes only 8 minutes !!
    from joblib import Parallel, delayed
    out_val_list = Parallel(n_jobs=10)(
        delayed(get_mention_from_wikilink_thrift_file)(fn)
        for fn in range(1, args.last_f2r))
    # out_val_list = [get_mention_from_wikilink_thrift_file(fn)
    #                 for fn in range(1, args.last_f2r)]

with rasengan.tictoc('Shelving'):
    import shelve
    from shelve import DbfilenameShelf
    total_data = defaultdict(list)
    for out_val in out_val_list:
        for url in out_val:
            total_data[url].extend(out_val[url])
    total_data.default_factory = None # FINALIZE out_val
    # Save the results of the processing.
    shelf = DbfilenameShelf(args.out_fn, protocol=-1)
    shelf['__URL_LIST__'] = total_data.keys()
    for url in shelf['__URL_LIST__']:
        shelf[url] = total_data[url]
    shelf.close()
    # Validation
    for e in POOL:
        assert e in total_data
