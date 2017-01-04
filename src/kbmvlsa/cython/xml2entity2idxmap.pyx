from cpython.unicode cimport PyUnicode_Tailmatch
from libcpp.string cimport string
from libcpp.unordered_map cimport unordered_map
cdef extern from "pyport.h" nogil:
    Py_ssize_t PY_SSIZE_T_MAX
import time, io, cPickle, config
from common import docno_matcher

cdef int main(str infn, str outfn):
    cdef:
        list storage = [u'']*300
        int doc_idx = 0
        unicode row = u''
        unicode document = u''
        int rows_in_storage = 0
        int i = 0
        unsigned long tic
        unordered_map[string,int] DOCNO_dict
    tic = time.time()
    for row in io.open(infn, mode='rt', encoding='utf8', errors='strict',
                       buffering=1000000):
        row = row.strip()
        storage[i] = row
        i += 1
        if PyUnicode_Tailmatch(row, u"</DOC>", 0, PY_SSIZE_T_MAX, 1) == 1:
            doc_idx += 1
            rows_in_storage = i
            i=0
            document = u' '.join(storage[:rows_in_storage])
            if doc_idx % 100000 == 0:
                print doc_idx, doc_idx / 95000.0, '%', (time.time() - tic)/60, 'min'
            docno = docno_matcher.match(document).group(1)
            DOCNO_dict[docno] = doc_idx
    with open(outfn, "wb") as f:
        cPickle.dump(DOCNO_dict, f, protocol=-1)
    return 1

def main_py(infn=config.TREC_WEB_DBPEDIA, outfn=config.TREC_WEB_DOCNO2ID_PKL):
    main(infn, outfn)