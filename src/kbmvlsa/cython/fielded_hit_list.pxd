from libcpp.vector cimport vector
from libcpp.pair cimport pair
from libcpp.string cimport string
cimport numpy as np
cdef class FieldedHitList:
    cdef readonly vector[vector[vector[pair[int,int]]]] field_token_doc_count
    cdef int update(FieldedHitList, int, int, int)
    cdef int _serialize(FieldedHitList,
        np.ndarray[np.uint32_t, ndim=1] arr,
        string arcname, zipf, string tmpfile_fn)
    cdef int my_serialize(FieldedHitList, string filename)
    cdef vector[vector[pair[int,int]]]* vec_ptr
    cdef vector[pair[int,int]]* vec2_ptr
    cdef int n_fields
    cdef list field_to_vocabsize

# def __cinit__(FieldedHitList, n_fields, field_to_vocabsize)
