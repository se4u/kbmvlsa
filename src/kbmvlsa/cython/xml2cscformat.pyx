# distutils: language=c++
'''
| Filename    : xml2tabsep.pyx
| Description : Convert XML file to a compressed collection of integers.
| Author      : Pushpendre Rastogi
| Created     : Wed Dec 21 00:03:06 2016 (-0500)
| Last-Updated: Sat Dec 24 18:54:29 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 182
It turns out that standard fgrep can zip through 12 GB of data in
15 minutes. Setting this as the benchmark, I want to convert the
trecweb file into a 5 collection of integers.
'''
import cPickle
import config
import io # codecs is crazy slow in comparison to the io module.
import os
import re
import time
import numpy as np
cimport numpy as np
from analyzer cimport c_analyze
from fielded_hit_list cimport FieldedHitList
from cpython.bytes cimport PyBytes_AS_STRING
from cpython.dict cimport PyDict_GetItemString, PyDict_SetItemString
from cpython.object cimport PyObject, PyObject_Hash
from cpython.unicode cimport PyUnicode_Tailmatch
from cython.operator cimport dereference as deref, postincrement
from libcpp.string cimport string
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector
cdef extern from "longobject.h" nogil:
    long PyLong_AsLong(PyObject *)
cdef extern from "Python.h":
    PyObject* Py_BuildValue(const char *, ...)
cdef extern from "numpy/npy_common.h" nogil:
    int NPY_MAX_UINT16
cdef extern from "pyport.h" nogil:
    Py_ssize_t PY_SSIZE_T_MAX

cdef vector[unordered_map[string,int]] load_field_token_index(
    string field_token_index_fn, int threshold):
    cdef vector[unordered_map[string,int]] field_token_index
    cdef unordered_map[string,int] mymap
    with open(field_token_index_fn) as f:
        data = cPickle.load(f)
    for e in data:
        mymap = dict((e_, i)
                     for i, (e_, e_count)
                     in enumerate(sorted(e.iteritems(),
                                         key=lambda x: (x[1], x[0]),
                                         reverse=True))
                     if e_count > threshold)
        field_token_index.push_back(mymap)
    return field_token_index

def main(args):
    tic = time.time()
    cdef unicode row
    cdef list storage = [u'']*300
    cdef int i = 0
    cdef int rows_in_storage = 0
    cdef unicode document
    cdef np.uint16_t unit_val = 1
    cdef int field_idx = 0
    cdef int doc_idx = -1
    cdef bytes token
    cdef np.uint16_t *tmp_np_count
    cdef vector[unordered_map[string,int]] field_token_index = \
        load_field_token_index(args.field_token_index_fn, args.threshold)
    cdef FieldedHitList hit_list = FieldedHitList(
        len(field_token_index),
        [len(e) for e in field_token_index])
    fast_re_pattern = '<%s> *(.+?) *</%s>.+?'
    re_pattern = ' *<DOC>.*?%s</DOC>'%(''.join(
        fast_re_pattern%(e, e)
        for e
        in ["DOCNO", "DOCHDR", "names", "category", "attributes", "SimEn", "RelEn"]))

    xml_matcher = re.compile(re_pattern)
    f = io.open(args.infn, mode='rt', encoding='utf8', errors='strict', buffering=1000000)
    cdef tuple fields
    cdef np.uint16_t* val_ptr
    cdef string token_string
    cdef vector[string] analyzed_field
    cdef unordered_map[string,int].iterator tmp_iter
    for row in f:
        row = row.strip()
        storage[i] = row
        i += 1
        if PyUnicode_Tailmatch(row, u"</DOC>", 0, PY_SSIZE_T_MAX, 1) == 1:
            doc_idx += 1
            rows_in_storage = i
            i=0
            document = u' '.join(storage[:rows_in_storage])
            if doc_idx % 10000 == 0:
                print doc_idx, doc_idx / 95000.0, '%', (time.time() - tic)/60, 'min'
                os.system("ps -o rss -o vsz " + str(os.getpid()))
            # print storage, document
            # DOCNO, DOCHDR, names, category, attributes, SimEn, RelEn
            fields = (xml_matcher.match(document).groups())
            for field_idx, field in enumerate(fields):
                analyzed_field = c_analyze(field)
                for token_string in analyzed_field:
                    tmp_iter = field_token_index[field_idx].find(token_string)
                    if tmp_iter != field_token_index[field_idx].end():
                        hit_list.update(field_idx,
                                        deref(tmp_iter).second,
                                        doc_idx)
    f.close()
    hit_list.my_serialize(args.outnpz)
    with open(args.outpkl, "wb") as f:
        cPickle.dump(field_token_index, f, protocol=-1)
    return

def parse_args():
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--infn', default=config.TREC_WEB_DBPEDIA, type=str)
    arg_parser.add_argument('--field_token_index_fn', default=config.TREC_WEB_TOKEN_PKL, type=str)
    arg_parser.add_argument('--threshold', default=2, type=int)
    arg_parser.add_argument('--outpkl', default=config.TREC_WEB_HIT_LIST_PKL, type=str)
    arg_parser.add_argument('--outnpz', default=config.TREC_WEB_HIT_LIST_NPZ, type=str)
    args=arg_parser.parse_args()
    print 'Reading input from', args.infn
    print 'Writing output to', args.outpkl, args.outnpz
    return args


if __name__ == '__main__':
    args = parse_args()
    main(args)

#  Local Variables:
#  eval: (python-mode)
#  End:
