#!/usr/bin/env python
'''
| Filename    : lib_view_transform.py
| Description : A Library of matrix transformations, with an enum and a getter.
| Author      : Pushpendre Rastogi
| Created     : Sun Dec  4 16:55:23 2016 (-0500)
| Last-Updated: Mon Dec  5 12:02:56 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 23
'''
from numpy import sqrt, log1p # pylint: disable=no-name-in-module
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import normalize
from class_pmi_transformer import PmiTransformer
from class_composable_transform import ComposableTransform

# These callables modify input *INPLACE*
callables = dict(
    IDENTITY=(lambda _: _),
    SQROOT=(lambda x: sqrt(x, out=x)), # pylint: disable=unnecessary-lambda
    LOG  =(lambda x: log1p(x, out=x)),
    # We don't copy data only if the original data was in `csr` format.
    # Otherwise, if the data was dense, or it was in csc format, we copy the data.
    TF   =(lambda x: TfidfTransformer(norm=None, use_idf=False, sublinear_tf=False).fit(x).transform(x, copy=False)),
    TFIDF=(lambda x: TfidfTransformer(norm=None, use_idf=True, sublinear_tf=False).fit(x).transform(x, copy=False)),
    NORM=(lambda x: normalize(x, norm='l2', axis=1, copy=False)),
    PMI=(lambda x: PmiTransformer()))

VT = ComposableTransform(
    callables,
    set('NORM IDENTITY LOG SQROOT '
        'TFIDF TF '
        'NORM_TFIDF NORM_TF '
        'SQROOT_TFIDF LOG_TFIDF'
        'PMI SHIFTEDPMI'.split()))

VTNS = VT.NS
