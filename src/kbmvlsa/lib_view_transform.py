#!/usr/bin/env python
'''
| Filename    : lib_view_transform.py
| Description : A Library of matrix transformations, with an enum and a getter.
| Author      : Pushpendre Rastogi
| Created     : Sun Dec  4 16:55:23 2016 (-0500)
| Last-Updated: Sun Dec  4 19:41:27 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 17
'''
from numpy import sqrt, log1p # pylint: disable=no-name-in-module
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import normalize

__NAMESPACE = set(
    'NORM IDENTITY LOG SQROOT '
    'TFIDF TF '
    'NORM_TFIDF NORM_TF '
    'SQROOT_TFIDF LOG_TFIDF'.split())

NS = Exception()
for e in __NAMESPACE:
    setattr(NS, e, e)

# These callables modify input *INPLACE*
__callables = dict(
    F_IDENTITY=(lambda _: _),
    F_SQROOT=(lambda x: sqrt(x, out=x)), # pylint: disable=unnecessary-lambda
    F_LOG  =(lambda x: log1p(x, out=x)),
    # We don't copy data only if the original data was in `csr` format.
    # Otherwise, if the data was dense, or it was in csc format, we copy the data.
    F_TF   =(lambda x: TfidfTransformer(norm=None, use_idf=False, sublinear_tf=False).fit(x).transform(x, copy=False)),
    F_TFIDF=(lambda x: TfidfTransformer(norm=None, use_idf=True, sublinear_tf=False).fit(x).transform(x, copy=False)),
    F_NORM=(lambda x: normalize(x, norm='l2', axis=1, copy=False)))

component_to_callable_map = {}

for k in __callables:
    name = k[2:]
    __callables[k].name = name
    component_to_callable_map[name] = __callables[k]

def compose(chain):
    def compose_impl(arg):
        for f in reversed(chain):
            arg = f(arg)
        return arg
    compose_impl.chain = chain
    return compose_impl

def parse(s):
    '''Take a string from __NAMESPACE and create a callable corresponding to it.
    The returned callable is capable of taking a matrix and modifying it inplace.
    '''
    assert s in __NAMESPACE
    callables = [component_to_callable_map[e]
                 for e in s.split('_')]
    return compose(callables)

def decompile(composition):
    return '_'.join(e.name for e in composition.chain)
