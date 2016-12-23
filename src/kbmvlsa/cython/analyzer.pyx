#!/usr/bin/env python
'''
| Filename    : analyzer.pyx
| Description : Analyzer converts strings to tokens
| Author      : Pushpendre Rastogi
| Created     : Mon Dec 19 21:16:02 2016 (-0500)
| Last-Updated: Fri Dec 23 17:24:59 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 62
In many situations, we may want to analyze a string,
by tokenizing it, lowercasing it, removing stop words,
and then stemming it. Doing all of this in python,
compositionally, through separate function calls can
cause a large, unnecessary, overheads. In this library
we remove that overhead by using cython and compiling
everything.
import string
class Analyzer(object):
    \'''
    Step 1: Tokenization (Spacy's tokenizer)
    Step 2: Transforming all tokens into lowercased ones
    Step 3: Whether to remove stop words
    Step 4: Whether to apply stemming
    \'''
    def __init__(self):
        self._tokenizer =
        self._stemmer = krovetzstemmer.Stemmer()
        self._numcleaner = dict((ord(e), u'0') for e in u'123456789')

    def replace_num(self, lot):
        return lot.translate(self._numcleaner)

    def stem(self, lot):
        return (self._stemmer(e) for e in lot)

    def filter_stop_words(self, lot):
        return (e for e in lot if e not in self._stop_words)

    def lowercase(self, lot):
        return (e.lower() for e in lot)

    def tokenize(self):
        return self._tokenizer()

    def __call__(self, string):
        return self.stem(self.filter_stop_words(self.lowercase(self.tokenize(string))))
'''
import re
import os.path
from itertools import chain
from libc.stdlib cimport malloc
from libcpp.vector cimport vector
from libcpp.string cimport string
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from string import punctuation, uppercase
from cpython.buffer cimport \
    PyBUF_SIMPLE, PyBUF_WRITABLE, \
    PyObject_CheckBuffer, PyObject_GetBuffer, PyBuffer_Release
from cpython.bytes cimport PyBytes_AS_STRING
from krovetzstemmer cimport KrovetzStemmer
cdef str exceptions_str = ".'%$&-" # Ensure that "-" comes last.
delete_runs_regex = re.compile(r"([%s])\1*"%exceptions_str)
remove_url_encoding = re.compile(r"%00")
cdef frozenset exceptions = frozenset(exceptions_str)
cdef frozenset replaced = frozenset(
    e for e in punctuation if e not in exceptions)
cdef dict translator = dict(chain(
    ((ord(e), u" ") for e in replaced),
    ((ord(e), u"0") for e in u"123456789"),
    ((ord(e), e.lower()) for e in unicode(uppercase))))

for resource_fn in ['res/indri_stop_words.txt', '../res/indri_stop_words.txt']:
    try:
        INDRI_STOP_WORDS = [unicode(e.strip())
                            for e
                            in open(resource_fn)]
    except IOError:
        pass

INDRI_STOP_WORDS.extend(["http", "dbpedia.org", "resource"])
cdef frozenset stop_words = frozenset(
    INDRI_STOP_WORDS
    + [unicode(e) for e in ENGLISH_STOP_WORDS])

cdef KrovetzStemmer *kstemmer = new KrovetzStemmer()
cdef char* temp_buffer = <char*>malloc(100 * sizeof(char))

# Ideally the following code should just work, however cython seems to have the
# problem that the coercion to typed memoryview is only done for writable buffers
# See: [http://stackoverflow.com/questions/28203670]
# (how-to-use-cython-typed-memoryviews-to-accept-strings-from-python)
# thankfully the SO page also suggests a worksround, using the CPython Api
# which I have implemented as the get_pointer function.
# UPDATE: I figured out the treasure trove of python c api
'''
cdef bytes stemmer(char[::1] s):
    print(s) # &s[0]
    cdef int written = kstemmer.kstem_stem_tobuffer(<char*>&s[0], temp_buffer)
    return bytes(temp_buffer[:written-1])

cdef inline char* get_pointer(bytes s):
    # assert PyObject_CheckBuffer(s), \
    #     "TypeError: argument must follow the buffer protocol"
    cdef Py_buffer view
    PyObject_GetBuffer(s, &view, PyBUF_SIMPLE)
    return <char*>view.buf
'''

cdef inline string stemmer(bytes s):
    cdef char* s_ptr = PyBytes_AS_STRING(s)
    cdef int written = kstemmer.kstem_stem_tobuffer(s_ptr, temp_buffer)
    return (string(s_ptr, len(s))
            if written == 0
            else string(temp_buffer, written-1))

cdef inline vector[string] stem_and_filter_stop_words(unicode s):
    cdef vector[string] ret_vec
    for e in s.encode('utf8').split():
        if e not in stop_words:
            ret_vec.push_back(stemmer(e))
    return ret_vec

cdef inline unicode delete_runs(unicode s):
    return remove_url_encoding.sub("",
                                   delete_runs_regex.sub(r"\1", s))

cdef inline unicode convert_punct_to_space_and_lowercase(unicode s):
    return s.translate(translator)

cdef inline vector[string] c_analyze(unicode s):
    return stem_and_filter_stop_words(
        delete_runs(convert_punct_to_space_and_lowercase(s)))

def analyze(s):
    return c_analyze(s)
