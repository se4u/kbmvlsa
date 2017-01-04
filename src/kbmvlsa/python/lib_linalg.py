#!/usr/bin/env python
'''
| Filename    : lib_linalg.py
| Description : Library of Linear Algebra functions
| Author      : Pushpendre Rastogi
| Created     : Mon Dec  5 12:33:48 2016 (-0500)
| Last-Updated: Wed Jan  4 14:12:14 2017 (-0500)
|           By: System User
|     Update #: 17
'''
import matrix_multiply_inplace
import numpy, os, scipy
import scipy.linalg
from rasengan import tictoc, print_config

def svd_1(a, debug=True, inplace=True):
    assert a.flags.c_contiguous
    if debug:
        print_config()
    # NOTE: scipy.linalg.blas.ssyrk(1, a, trans=1, lower=1)
    # causes an unnecessary copy, because a is c_contiguous.
    with tictoc('Computing b'):
        b = scipy.linalg.blas.ssyrk(1, a.T, trans=0, lower=1)
    if debug:
        print_config()
    with tictoc('Computing eigh'):
        [bs, bu] = scipy.linalg.eigh(b, turbo=True, overwrite_a=True,
                                     check_finite=True)
    with tictoc('Scale bu inplace'):
        for i in xrange(bu.shape[1]-1, -1, -1):
            scalar = (1/numpy.sqrt(bs[i])
                      if bs[i] > 1e-6
                      else 0)
            scipy.linalg.blas.sscal(scalar, bu, n=bu.shape[0], offx=i*bu.shape[0])
    if debug:
        print_config(msg='i=%d'%i)
    with tictoc('Inplace Matmul'):
        c = matrix_multiply_inplace.matmul(a, bu)
    del bu
    del bs
    if debug:
        print_config()
    return [c, i]
