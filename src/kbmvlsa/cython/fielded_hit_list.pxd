from libcpp.vector cimport vector
from libcpp.pair cimport pair

cdef class FieldedHitList:
    cdef readonly vector[vector[vector[pair[int,int]]]] field_token_doc_count
    cdef int update(FieldedHitList, int, int, int)
    cdef vector[vector[pair[int,int]]]* vec_ptr
    cdef vector[pair[int,int]]* vec2_ptr

# def __cinit__(FieldedHitList, n_fields, field_to_vocabsize)
