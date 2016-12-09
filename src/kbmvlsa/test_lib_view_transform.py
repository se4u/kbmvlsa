#!/usr/bin/env python
'''
| Filename    : test_lib_view_transform.py
| Description : Test that the transformation library works as expected.
| Author      : Pushpendre Rastogi
| Created     : Sun Dec  4 18:01:11 2016 (-0500)
| Last-Updated: Mon Dec  5 12:03:31 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 37
'''
import numpy
data = numpy.array([[6, 8, 4], [9, 5, 7], [3, 8, 5], [4, 0, 8], [8, 7, 7]], dtype='float32')
data_copy = numpy.copy(data)
from lib_view_transform import VT, VTNS

for transform, gold_output in [
        (VTNS.TFIDF, [[ 6., 9.45857245, 4.], [ 9., 5.91160778, 7.], [ 3., 9.45857245, 5.], [ 4., 0., 8.], [ 8., 8.2762509, 7.]]),
        (VTNS.NORM, [[0.55708601, 0.74278135, 0.37139068], [ 0.7228974,  0.40160966, 0.56225353], [ 0.30304576, 0.80812204, 0.50507627], [ 0.4472136,  0., 0.89442719], [ 0.62853936, 0.54997194, 0.54997194]]),
        (VTNS.NORM_TFIDF, [[ 0.50446074,  0.79524641 , 0.33630716], [ 0.70076138,  0.46029182 , 0.54503663], [ 0.26999147,  0.85124462 , 0.44998578], [ 0.4472136 ,  0.         , 0.89442719], [ 0.5938217 ,  0.61432717 , 0.51959399]]),
        (VTNS.LOG, [[ 1.9459101  , 2.19722462 , 1.60943794], [ 2.30258512 , 1.79175949 , 2.07944155], [ 1.38629436 , 2.19722462 , 1.79175949], [ 1.60943794 , 0.         , 2.19722462], [ 2.19722462 , 2.07944155 , 2.07944155]])]:
    f = VT.parse(transform)
    assert transform == VT.decompile(f)
    output = f(data)
    try:
        numpy.testing.assert_allclose(
            output, numpy.array(gold_output, dtype='float32'), rtol=1e-4)
    except:
        numpy.testing.assert_allclose(
            output.todense(), numpy.array(gold_output, dtype='float32'), rtol=1e-4)
    data[:] = data_copy
print "Check Complete"
