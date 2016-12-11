#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : util_trecweb_parser.py
| Description : Parse the trecweb format files provided by Chen and Xiong
| Author      : Pushpendre Rastogi
| Created     : Thu Dec  8 19:39:09 2016 (-0500)
| Last-Updated: Sun Dec 11 04:45:16 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 160
'''
import xml.sax
import config
import sys
import itertools
from rasengan import tictoc, StreamingArrayMaker, print_proc_info

TOPLEVEL_ELEM_NAME = 'XML'
ROW_ELEM_NAME = 'DOC'
DOCID_FIELD = 'DOCHDR'
ARRAY_MAKER = None

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
            ARRAY_MAKER.update_1(docid, cat_data)
            self.lastEntry = None
        elif name == TOPLEVEL_ELEM_NAME:
            raise StopIteration
        return

    def characters(self, content):
        if self.lastEntry:
            self.lastEntry[self.lastName.strip()].append(content)
        return


def main(dbpedia_fn):
    print 'Will save output to', config.TREC_WEB_DBPEDIA_PFX
    parser = xml.sax.make_parser()
    parser.setContentHandler(StreamHandler())
    global ARRAY_MAKER
    with tictoc('Initializing Array Maker'):
        ARRAY_MAKER = StreamingArrayMaker(config.TREC_WEB_CATEGORIES,
                                          default_shape=(10000000, 100000000))
    if dbpedia_fn.endswith('zip'):
        import zipfile
        dbpedia_file = zipfile.ZipFile(dbpedia_fn)\
                              .open('dbpedia.trecweb')
    elif dbpedia_fn.endswith('gz'):
        import gzip
        dbpedia_file = gzip.open(dbpedia_fn)
    counter = 0
    for buffer_ in itertools.chain(['<XML>'], iter(dbpedia_file), ['</XML>']):
        if buffer_:
            counter += 1
            if counter%100000 == 0:
                print counter
            try:
                buffer_ = buffer_.replace('&', '&amp;').strip()
                if not buffer_.endswith('>'):  # len(buffer_) > 100
                    buffer_ = buffer_.replace('<', '&lt;')
                parser.feed(buffer_)
            except StopIteration:
                break
            except xml.sax._exceptions.SAXParseException:
                print >> sys.stderr, 'Error:'
                print >> sys.stderr, buffer_
                break
    with tictoc('Finalizing'):
        ARRAY_MAKER.finalize()
    with tictoc('Saving'):
        ARRAY_MAKER.save_to_pfx(config.TREC_WEB_DBPEDIA_PFX)
    return

if __name__ == '__main__':
    print_proc_info()
    main(config.TREC_WEB_DBPEDIA_GZ)
