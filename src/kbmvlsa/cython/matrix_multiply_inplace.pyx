'''
| Filename    : matrix_multiply_inplace.pyx
| Description : Perform inplace matrix multiplication
| Author      : Pushpendre Rastogi
| Created     : Sun Jan  1 22:43:06 2017 (-0500)
| Last-Updated: Mon Jan  2 12:09:58 2017 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 12
'''
cimport scipy.linalg.cython_blas as blas
cimport cython
import numpy as np
cimport numpy as np

@cython.initializedcheck(False)
@cython.wraparound(False)
@cython.boundscheck(False)
@cython.overflowcheck(False)
cdef np.ndarray[float,ndim=2] matrix_multiply_impl1(
    np.ndarray[float,ndim=2] a,
    np.ndarray[float,ndim=2] b):
    cdef:
        unsigned int i = 0
        char trans = 't'
        int m=b.shape[0], n=b.shape[1], incx=1, incy=1
        int lda=m
        float alpha=1, x, beta=0
        np.ndarray[float,ndim=1] y = np.zeros((m,), dtype='float32', order='C')
    for i in range(a.shape[0]):
        # (char *trans, int *m, int *n, float *alpha, float *a, int *lda, float *x, int *incx, float *beta, float *y, int *incy)
        blas.sgemv(&trans, &m, &n, &alpha, &b[0, 0], &lda, &a[i,0], &incx, &beta, &y[0], &incy)
        a[i,:] = y
    return a


def matmul(a, b):
    assert a.flags.c_contiguous
    assert b.flags.f_contiguous
    return matrix_multiply_impl1(a,b)
