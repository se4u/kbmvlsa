# distutils: language=c++
from libcpp.vector cimport vector
from libcpp.pair cimport pair
from libcpp.string cimport string
from cython.operator cimport dereference as deref, postincrement
import numpy as np
import numpy.lib
cimport numpy as np
import zipfile
import os, tempfile
cimport cython

cdef class FieldedHitList:
    "A Cython class to store a HitList"
    def __cinit__(self, int n_fields, list field_to_vocabsize):
        self.n_fields = n_fields
        self.field_to_vocabsize = field_to_vocabsize
        for f, vocabsize in zip(range(n_fields), field_to_vocabsize):
            vec_ptr = new vector[vector[pair[int,int]]]()
            for v in range(vocabsize):
                vec2_ptr = new vector[pair[int,int]]()
                # print vec2_ptr.size()
                deref(vec_ptr).push_back(deref(vec2_ptr))
            self.field_token_doc_count.push_back(deref(vec_ptr))
        return

    cdef int update(self, int field_idx, int token_idx, int doc_idx):
        cdef pair[int,int]* topelem_ptr
        cdef vector[pair[int,int]]* ft_ptr = &(
            self.field_token_doc_count[field_idx][token_idx])
        cdef int retval
        if deref(ft_ptr).size():
            # print field_idx, token_idx, doc_idx, deref(ft_ptr)
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
        # print field_idx, token_idx, doc_idx, deref(ft_ptr)
        return retval


    cdef int _serialize(self,
                        np.ndarray[np.uint32_t, ndim=1] arr,
                        string arcname,
                        zipf,
                        string tmpfile_fn):
        ''' Save `array` to `zipf` with `arcname` in two steps.
        1st write `arr` to `tmpfile_fn`.
        2nd add the `tmpfile_fn` to `zipf` under the name `arcname`
        '''
        with open(tmpfile_fn, 'wb') as tmpfile:
            numpy.lib.format.write_array(tmpfile, arr, allow_pickle=False)
        zipf.write(tmpfile_fn, arcname=arcname)
        return 0

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef int my_serialize(self, string filename):
        cdef int field_idx
        cdef np.ndarray[np.uint32_t, ndim=1] indptr
        cdef np.ndarray[np.uint32_t, ndim=1] indices
        cdef np.ndarray[np.uint32_t, ndim=1] data
        cdef int data_size
        cdef int vocab_size
        cdef int data_idx
        cdef int offset_idx
        cdef vector[pair[int,int]]* column_ptr
        cdef string arcname
        with zipfile.ZipFile(filename, mode="w", compression=zipfile.ZIP_STORED,
                             allowZip64=True) as zipf:
            for field_idx in range(self.n_fields):
                vocab_size = self.field_token_doc_count[field_idx].size()
                indptr = np.empty([vocab_size,], dtype=np.uint32)
                data_size = 0
                for token_idx in range(vocab_size):
                    indptr[token_idx] = self.field_token_doc_count[field_idx][token_idx].size()
                    data_size += indptr[token_idx]

                print field_idx, data_size
                indices = np.empty([data_size,], dtype=np.uint32)
                data = np.empty([data_size,], dtype=np.uint32)
                data_idx = -1
                for token_idx in range(vocab_size):
                    column_ptr = &self.field_token_doc_count[field_idx][token_idx]
                    for offset_idx in range(indptr[token_idx]):
                        data_idx += 1
                        indices[data_idx] = (deref(column_ptr))[offset_idx].first
                        data[data_idx] = (deref(column_ptr))[offset_idx].second
                file_dir, file_prefix = os.path.split(filename)
                tmpfd, tmpfile_fn = tempfile.mkstemp(prefix=file_prefix, dir=file_dir, suffix='-numpy.npy')
                os.close(tmpfd)
                arcname = str(field_idx) + '_indptr'
                self._serialize(indptr, arcname, zipf, tmpfile_fn)
                arcname = str(field_idx) + '_indices'
                self._serialize(indices, arcname, zipf, tmpfile_fn)
                arcname = str(field_idx) + '_data'
                self._serialize(data, arcname, zipf, tmpfile_fn)
        return 0
