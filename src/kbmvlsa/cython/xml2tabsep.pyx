# distutils: language=c++
'''
| Filename    : xml2tabsep.pyx
| Description : Convert XML file to a compressed collection of integers.
| Author      : Pushpendre Rastogi
| Created     : Wed Dec 21 00:03:06 2016 (-0500)
| Last-Updated: Sat Dec 24 22:15:15 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 149
It turns out that standard fgrep can zip through 12 GB of data in
15 minutes. Setting this as the benchmark, I want to convert the
trecweb file into a 5 collection of integers.
'''
import cPickle
# codecs is crazy slow in comparison to the io module.
# The codecs module took 3.5 seconcs whereas io uses < .1s
import io
import config
import time
import numpy as np
cimport numpy as np
from analyzer cimport c_analyze
from cpython.unicode cimport PyUnicode_Tailmatch
from cpython.dict cimport PyDict_GetItemString, PyDict_SetItemString
from cpython.bytes cimport PyBytes_AS_STRING
from cpython.object cimport PyObject, PyObject_Hash
from cython.operator cimport dereference as deref, postincrement
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector
from libcpp.string cimport string
cdef extern from "longobject.h" nogil:
    long PyLong_AsLong(PyObject *)
cdef extern from "Python.h":
    PyObject* Py_BuildValue(const char *, ...)
cdef extern from "numpy/npy_common.h" nogil:
    int NPY_MAX_UINT16
cdef extern from "pyport.h" nogil:
    Py_ssize_t PY_SSIZE_T_MAX

def main(args):
    cdef unicode row
    cdef list storage = [u'']*300
    cdef int i = 0
    cdef int rows_in_storage = 0
    cdef unicode document
    cdef np.uint16_t unit_val = 1
    cdef vector[unordered_map[string,np.uint16_t]] dict_list
    cdef unordered_map[string,np.uint16_t] DOCNO_dict
    dict_list.push_back(DOCNO_dict)
    cdef unordered_map[string,np.uint16_t] DOCHDR_dict
    dict_list.push_back(DOCHDR_dict)
    cdef unordered_map[string,np.uint16_t] names_dict
    dict_list.push_back(names_dict)
    cdef unordered_map[string,np.uint16_t] category_dict
    dict_list.push_back(category_dict)
    cdef unordered_map[string,np.uint16_t] attributes_dict
    dict_list.push_back(attributes_dict)
    cdef unordered_map[string,np.uint16_t] SimEn_dict
    dict_list.push_back(SimEn_dict)
    cdef unordered_map[string,np.uint16_t] RelEn_dict
    dict_list.push_back(RelEn_dict)
    cdef int field_idx = 0
    cdef int doc_idx = -1
    cdef bytes token
    cdef np.uint16_t *tmp_np_count
    fast_re_pattern = '<%s> *(.+?) *</%s>.+?'
    re_pattern = ' *<DOC>.*?%s</DOC>'%(''.join(
        fast_re_pattern%(e, e)
        for e
        in config.TREC_WEB_CATEGORIES))
    import re
    xml_matcher = re.compile(re_pattern)
    tic = time.time()
    f = io.open(args.infn, mode='rt', encoding='utf8', errors='strict', buffering=1000000)
    cdef tuple fields
    cdef np.uint16_t* val_ptr
    cdef string token_string
    cdef vector[string] analyzed_field
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
            # print storage, document
            # DOCNO, DOCHDR, names, category, attributes, SimEn, RelEn
            fields = (xml_matcher.match(document).groups())
            for field_idx, field in enumerate(fields):
                analyzed_field = c_analyze(field)
                for token_string in analyzed_field:
                    val_ptr = &(dict_list[field_idx][token_string])
                    if deref(val_ptr) == NPY_MAX_UINT16:
                        continue
                    else:
                        postincrement(deref(val_ptr))
                    # print field_idx, token_string, dict_list[field_idx][token_string]
    f.close()
    return dict_list

def parse_args():
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--infn', default=config.TREC_WEB_DBPEDIA, type=str)
    arg_parser.add_argument('--outfn', default=config.TREC_WEB_TOKEN_PKL, type=str)
    args=arg_parser.parse_args()
    print 'Reading input from', args.infn
    print 'Writing output to', args.outfn
    return args

def save(args, dict_list):
    with open(args.outfn, "wb") as f:
        cPickle.dump(dict_list, f, protocol=-1)

if __name__ == '__main__':
    args = parse_args()
    dict_list = main(args)
    save(args, dict_list)

#  Local Variables:
#  eval: (python-mode)
#  End:
