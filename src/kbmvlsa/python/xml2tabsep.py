#!/usr/bin/env python
'''
| Filename    : xml2tabsep.py
| Description : Convert Trecweb format to Tab Separated format so that we don't
                need SAX api and other slow code.
| Author      : Pushpendre Rastogi
| Created     : Mon Dec 19 12:27:46 2016 (-0500)
| Last-Updated: Tue Dec 20 23:36:42 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 34
'''
import re, sys, codecs, config
from rasengan import groupby
import string
import argparse
import pdb
from analyzer import analyze
xml_matcher = re.compile('.*?%s</DOC>'%(''.join(
    '<%s> *(.+?) *</%s>.+?'%(e, e)
    for e
    in ["DOCNO", "DOCHDR", "names", "category", "attributes", "SimEn", "RelEn"])))
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--infn', default=config.TREC_WEB_DBPEDIA, type=str)
args=arg_parser.parse_args()

def main_loop():
    with codecs.open(args.infn, mode='rb', encoding='utf8', errors='strict') as f:
        for idx_doc, data in enumerate(groupby(f, predicate=lambda x: not x.startswith("<DOC>"), yield_iter=True)):
            data = ' '.join(e.replace('\n', ' ') for e in data)
            fields = [analyze(match) for match in xml_matcher.match(data).groups()]
            yield idx_doc, fields

def count_tokens():
    d = set()
    for idx_doc, fields in main_loop():
        [d.update(f) for f in fields]
    print idx_doc, len(d)

def count_docs():
    with codecs.open(args.infn, mode='rb', encoding='utf8', errors='strict') as f:
        print sum(1
                  for e
                  in groupby(f,
                             predicate=lambda x: not x.startswith("<DOC>"),
                             yield_iter=True))

if __name__ == '__main__':
    count_docs()
    # count_tokens()
