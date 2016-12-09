#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : util_trecweb_parser.py
| Description : Parse the trecweb format files provided by Chen and Xiong
| Author      : Pushpendre Rastogi
| Created     : Thu Dec  8 19:39:09 2016 (-0500)
| Last-Updated: Fri Dec  9 12:44:32 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 71
'''
import xml.sax
import config
import sys
import itertools
import zipfile
import cPickle as pickle
from rasengan import TokenMapper, PUNCT_CHAR, REGEX_SPECIAL_CHAR, ConstantList
import re
import scipy
TOPLEVEL_ELEM_NAME = 'XML'
ROW_ELEM_NAME = 'DOC'
DOCID_FIELD = 'DOCHDR'
ARRAY_MAKER = None
PUNCT_MATCH_REGEX = re.compile(
    '([%s])'%(''.join(
        ('\\%s'%e if e in REGEX_SPECIAL_CHAR else e)
        for e
        in PUNCT_CHAR)))
# BUFFER_END_REGEX = re.compile('^.*(XML|DOC|DOCNO|DOCHDR|names|category|attributes|SimEn|RelEn)>$')

class StreamingArrayMaker(object):
    def __init__(self, ):
        self.arr_list = [([], [])
                         for e
                         in config.TREC_WEB_CATEGORIES]
        self.ent_map = TokenMapper()
        self.tm_list = [TokenMapper() for e in config.TREC_WEB_CATEGORIES]
        return

    def tokenize(self, s):
        return [e for e in re.split(PUNCT_MATCH_REGEX, s) if e != '']

    def process(self, docid, cat_data):
        doc_int = self.ent_map([docid])[0]
        for i, cat in enumerate(config.TREC_WEB_CATEGORIES):
            data = self.tm_list[i](self.tokenize(cat_data[i]))
            self.arr_list[i][0].append(doc_int)
            self.arr_list[i][1].extend(data)
        return

    def finalize(self):
        for i in range(len(config.TREC_WEB_CATEGORIES)):
            data = ConstantList(1, len(self.arr_list[i][0]))
            self.arr_list[i] = scipy.sparse.coo_matrix(
                (data, self.arr_list[i]))


class StreamHandler(xml.sax.handler.ContentHandler):
    ''' Sax API based XML parser based on the code at
    stackoverflow.com/questions/7693535
    what-is-a-good-xml-stream-parser-for-python
    '''
    lastEntry = None
    lastName = None

    def startElement(self, name, attrs):
        self.lastName = name.strip()
        if name == ROW_ELEM_NAME:
            self.lastEntry = {}
        elif name != TOPLEVEL_ELEM_NAME:
            self.lastEntry[name] = []
        return

    def endElement(self, name):
        if name == ROW_ELEM_NAME:
            assert (DOCID_FIELD in self.lastEntry)
            docid = ''.join(self.lastEntry[DOCID_FIELD]).strip()
            cat_data = [''.join(self.lastEntry[cat]).strip()
                        for cat
                        in config.TREC_WEB_CATEGORIES]
            # -------------------------------------------------- #
            # We call ARRAY_MAKER.process to update the matrix . #
            # -------------------------------------------------- #
            # ARRAY_MAKER.process(docid, cat_data)
            self.lastEntry = None
        elif name == TOPLEVEL_ELEM_NAME:
            raise StopIteration
        return

    def characters(self, content):
        if self.lastEntry:
            self.lastEntry[self.lastName.strip()].append(content)
        return


if __name__ == '__main__':
    # use default ``xml.sax.expatreader``
    parser = xml.sax.make_parser()
    parser.setContentHandler(StreamHandler())
    ARRAY_MAKER = StreamingArrayMaker()
    dbpedia_file = zipfile.ZipFile(config.TREC_WEB_DBPEDIA_ZIP)\
                          .open('dbpedia.trecweb')
    for buffer_ in itertools.chain(['<XML>'], iter(dbpedia_file), ['</XML>']):
        if buffer_:
            try:
                buffer_ = buffer_.replace('&', '&amp;')
                if not buffer_.endswith('>'):
                    buffer_ = buffer_.replace('<', '&lt;')
                # print buffer_
                parser.feed(buffer_)
            except StopIteration:
                break
            except xml.sax._exceptions.SAXParseException:
                print >> sys.stderr, 'Error:'
                print >> sys.stderr, buffer_
                break
    import pdb
    pdb.set_trace()
    ARRAY_MAKER.finalize()
    with open(config.TREC_WEB_DBPEDIA_PKL, 'wb') as f:
        pickle.dump(ARRAY_MAKER, f, protocol=-1)
    pass
