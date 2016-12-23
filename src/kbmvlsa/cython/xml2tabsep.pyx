'''
| Filename    : xml2tabsep.pyx
| Description : Convert XML file to a compressed collection of integers.
| Author      : Pushpendre Rastogi
| Created     : Wed Dec 21 00:03:06 2016 (-0500)
| Last-Updated: Fri Dec 23 02:16:53 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 125
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
from libcpp.vector cimport vector
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
    cdef int doc_idx = -1
    cdef bytes token
    cdef np.uint16_t *tmp_np_count
    cdef np.uint16_t val
    fast_re_pattern = '<%s> *(.+?) *</%s>.+?'
    re_pattern = ' *<DOC>.*?%s</DOC>'%(''.join(
        fast_re_pattern%(e, e)
        for e
        in ["DOCNO", "DOCHDR", "names", "category", "attributes", "SimEn", "RelEn"]))
    import re
    xml_matcher = re.compile(re_pattern)
    tic = time.time()
    f = io.open(args.infn, mode='rt', encoding='utf8', errors='strict', buffering=1000000)
    cdef tuple fields
    cdef PyObject* debug_a
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
                for token in c_analyze(field):
                    debug_a = PyDict_GetItemString(<dict>(dict_list[field_idx]),
                                                            PyBytes_AS_STRING(token))
                    if debug_a != NULL:
                        val = PyLong_AsLong(debug_a)
                        if val == NPY_MAX_UINT16:
                            continue
                        else:
                            val += 1
                    else:
                        val = 1
                    PyDict_SetItemString(
                        dict_list[field_idx],
                        PyBytes_AS_STRING(token),
                        <object>Py_BuildValue("H", val))
                    # print field_idx, token, dict_list[field_idx][token]
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
