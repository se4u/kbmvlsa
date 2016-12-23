# distutils: language=c++
'''
| Filename    : analyzer.pxd
| Description : Header providng c_analysis functions
| Author      : Pushpendre Rastogi
| Created     : Wed Dec 21 03:37:55 2016 (-0500)
| Last-Updated: Wed Dec 21 03:39:24 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 1
'''
from libcpp.string cimport string
from libcpp.vector cimport vector
cdef vector[string] c_analyze(unicode)
