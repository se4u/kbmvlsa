#!/usr/bin/env python
'''
| Filename    : xml2tabsep.pyx
| Description : Convert XML file to a compressed collection of integers.
| Author      : Pushpendre Rastogi
| Created     : Wed Dec 21 00:03:06 2016 (-0500)
| Last-Updated: Wed Dec 21 05:58:28 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 38
It turns out that standard fgrep can zip through 12 GB of data in
15 minutes. Setting this as the benchmark, I want to convert the
trecweb file into a 5 collection of integers.


import re, sys, codecs, config
from rasengan import groupby
import string
import argparse
import pdb
from analyzer import analyze

arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--infn', default=config.TREC_WEB_DBPEDIA, type=str)
args=arg_parser.parse_args()

def main_loop():
    with codecs.open(args.infn, mode='rb', encoding='utf8', errors='strict') as f:
        for idx_doc, data in enumerate(groupby(f, predicate=lambda x: not x.startswith("<DOC>"), yield_iter=True)):
            data = ' '.join(e.replace('\n', ' ') for e in data)
            fields = [analyze(match) for match in xml_matcher.match(data).groups()]
            yield idx_doc, fields
'''
import codecs, time
cimport numpy as np
from analyzer cimport c_analyze
from cpython.dict cimport PyDict_GetItemString, PyDict_SetItemString
from cpython.bytes cimport PyBytes_AS_STRING
from cpython.object cimport PyObject, PyObject_Hash
from libcpp.vector cimport vector
# import config
import numpy as np
import re
# config.TREC_WEB_DBPEDIA
f = codecs.open("/Users/pushpendrerastogi/data/chen-xiong-EntityRankData"
                "/dbpedia.trecweb/dbpedia.trecweb",
                mode='rb', encoding='utf8', errors='strict')
cdef unicode row
cdef list storage = [u'']*300
cdef int i = 0
cdef int rows_in_storage = 0
cdef unicode document
cdef np.uint8_t unit_i8 = 1
cdef dict DOCNO_dict = {}
cdef dict DOCHDR_dict = {}
cdef dict names_dict = {}
cdef dict category_dict = {}
cdef dict attributes_dict = {}
cdef dict SimEn_dict = {}
cdef dict RelEn_dict = {}
cdef list dict_list = [DOCNO_dict, DOCHDR_dict, names_dict, category_dict,
                       attributes_dict, SimEn_dict, RelEn_dict]
cdef int field_idx = 0
cdef int doc_count = 0
cdef bytes token
cdef np.uint8_t *tmp_np_count
xml_matcher = re.compile(' *<DOC>.*?%s</DOC>'%(''.join(
    '<%s> *(.+?) *</%s>.+?'%(e, e)
    for e
    in ["DOCNO", "DOCHDR", "names", "category", "attributes", "SimEn", "RelEn"])))
tic = time.time()
for row in f:
    row = row.strip()
    storage[i] = row
    i += 1
    if row.endswith("</DOC>"):
        doc_count += 1
        rows_in_storage = i
        i=0
        document = u' '.join(storage[:rows_in_storage])
        if doc_count % 10000 == 0:
            print doc_count, doc_count / 95000.0, '%', (time.time() - tic)/60, 'min'
        # print storage, document
        # DOCNO, DOCHDR, names, category, attributes, SimEn, RelEn
        fields = xml_matcher.match(document).groups()
        for field_idx, field in enumerate(fields):
            for token in c_analyze(field):
                tmp_np_count = <np.uint8_t*>(PyDict_GetItemString(
                    <dict>(dict_list[field_idx]),
                    PyBytes_AS_STRING(token)))
                PyDict_SetItemString(
                    <dict>(dict_list[field_idx]),
                    PyBytes_AS_STRING(token),
                    (1 if tmp_np_count == NULL else tmp_np_count[0] + 1))