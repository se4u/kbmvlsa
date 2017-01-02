#!/usr/bin/env python
'''
| Filename    : lib_linalg.py
| Description : Library of Linear Algebra functions
| Author      : Pushpendre Rastogi
| Created     : Mon Dec  5 12:33:48 2016 (-0500)
| Last-Updated: Mon Jan  2 15:13:29 2017 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 13
'''
import matrix_multiply_inplace
import numpy, os, scipy
import scipy.linalg

def print_config(numpy=0, hostname=0, ps=0):
    if numpy:
        numpy.show_config()
    pid = os.getpid()
    print 'pid', pid
    import subprocess
    cmd = ("ps uf %d;"%pid if ps else "")
    cmd += " grep '[TV][hm][rHRS][eSWw]' /proc/%d/status; "%pid
    if hostname:
        cmd += "echo hostname `hostname`"
    print subprocess.check_output(
        [cmd],
        stderr=subprocess.STDOUT,
        shell=True)
    return

def svd_1(a, debug=False, inplace=True):
    assert a.flags.c_contiguous
    if debug:
        print_config()
    # NOTE: scipy.linalg.blas.ssyrk(1, a, trans=1, lower=1)
    # causes an unnecessary copy, because a is c_contiguous.
    b = scipy.linalg.blas.ssyrk(1, a.T, trans=0, lower=1)
    if debug:
        print_config()
    [bs, bu] = scipy.linalg.eigh(
        b,
        turbo=True,
        overwrite_a=True,
        check_finite=True)
    # Scale bu inplace
    for i in xrange(bu.shape[1]-1, -1, -1):
        scalar = (1/numpy.sqrt(bs[i])
                  if bs[i] > 1e-6
                  else 0)
        scipy.linalg.blas.sscal(scalar, bu, n=bu.shape[0], offx=i*bu.shape[0])
    if debug:
        print 'i', i
        print_config()
    c = matrix_multiply_inplace.matmul(a, bu)
    del bu
    del bs
    if debug:
        print_config()
    return [c, i]
