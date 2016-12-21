#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : util_trecweb_parser.py
| Description : Parse the trecweb format files provided by Chen and Xiong
| Author      : Pushpendre Rastogi
| Created     : Thu Dec  8 19:39:09 2016 (-0500)
| Last-Updated: Sun Dec 11 19:23:27 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 182
'''
import xml.sax
import config
import sys
import itertools
from rasengan import tictoc, StreamingArrayMaker, print_proc_info

TOPLEVEL_ELEM_NAME = 'XML'
ROW_ELEM_NAME = 'DOC'
# DOCID_FIELD = 'DOCNO'
DOCID_FIELD = 'DOCHDR'
ARRAY_MAKER = None

class StreamHandler(xml.sax.handler.ContentHandler):
    ''' Sax API based XML parser based on the code at
    stackoverflow.com/questions/7693535
    what-is-a-good-xml-stream-parser-for-python
    '''
    lastEntry = None
    lastName = None
    field_func = None

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
            self.field_func(docid, cat_data)
            self.lastEntry = None
        elif name == TOPLEVEL_ELEM_NAME:
            raise StopIteration
        return

    def characters(self, content):
        if self.lastEntry:
            self.lastEntry[self.lastName.strip()].append(content)
        return

from string import maketrans
translator = maketrans("\n", " ")
uTranslator = {u'\n': u' '}
def print_cat(docid, cat_data):
    print_sep = (len(args.cat_to_print) > 1)
    if args.print_docid:
        print docid,
    for i, cat in enumerate(config.TREC_WEB_CATEGORIES):
        if cat in args.cat_to_print:
            if print_sep:
                print '|||',
            if args.print_cat_name:
                print cat,
            if isinstance(cat_data[i],unicode):
                print cat_data[i].translate(uTranslator),
            else:
                print cat_data[i].translate(translator),
    print

def open_compressed_file(fn):
    if fn.endswith('zip'):
        import zipfile
        return zipfile.ZipFile(fn).open('dbpedia.trecweb')
    elif fn.endswith('gz'):
        import gzip
        return gzip.open(fn)
    else:
        raise NotImplementedError()


def prepare_stream_handler():
    stream_handler = StreamHandler()
    if args.cat_to_print is None:
        with tictoc('Initializing Array Maker'):
            global ARRAY_MAKER
            ARRAY_MAKER = StreamingArrayMaker(
                config.TREC_WEB_CATEGORIES,
                default_shape=(10000000, 100000000))
        stream_handler.field_func = ARRAY_MAKER.update_1
    else:
        stream_handler.field_func = print_cat
    return stream_handler


def main():
    dbpedia_fn = config.TREC_WEB_DBPEDIA_GZ
    parser = xml.sax.make_parser()
    stream_handler = prepare_stream_handler()
    parser.setContentHandler(stream_handler)
    dbpedia_file = open_compressed_file(dbpedia_fn)
    counter = 0
    parser.feed('<XML>')
    for buffer_ in dbpedia_file:
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
        print 'Will save output to', config.TREC_WEB_DBPEDIA_PFX
        ARRAY_MAKER.save_to_pfx(config.TREC_WEB_DBPEDIA_PFX)
    return


if __name__ == '__main__':
    print_proc_info()
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--cat_to_print', nargs='+', default=None)
    arg_parser.add_argument('--print_cat_name', default=0, type=int)
    arg_parser.add_argument('--print_docid', default=0, type=int)
    args=arg_parser.parse_args()
    if args.cat_to_print is not None:
        args.cat_to_print = set(args.cat_to_print)
    main()
