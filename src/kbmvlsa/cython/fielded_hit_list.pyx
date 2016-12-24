# distutils: language=c++
from libcpp.vector cimport vector
from libcpp.pair cimport pair
from cython.operator cimport dereference as deref, postincrement

cdef class FieldedHitList:
    "A Cython class to store a HitList"
    def __cinit__(self, n_fields, field_to_vocabsize):
        for f, vocabsize in zip(range(n_fields), field_to_vocabsize):
            vec_ptr = new vector[vector[pair[int,int]]]()
            for v in range(vocabsize):
                vec2_ptr = new vector[pair[int,int]]()
                deref(vec_ptr).push_back(deref(vec2_ptr))
            self.field_token_doc_count.push_back(deref(vec_ptr))
        return

    cdef int update(self, int field_idx, int token_idx, int doc_idx):
        cdef pair[int,int]* topelem_ptr
        cdef vector[pair[int,int]]* ft_ptr = &(
            self.field_token_doc_count[field_idx][token_idx])
        cdef int retval
        if deref(ft_ptr).size():
            topelem_ptr = &(deref(ft_ptr).back())
            if deref(topelem_ptr).first == doc_idx:
                postincrement(deref(topelem_ptr).second)
                retval = 0
            else:
                deref(ft_ptr).push_back((doc_idx, 1))
                retval = 1
        else:
            deref(ft_ptr).push_back((doc_idx, 1))
            retval = 1
        return retval