#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : class_pmi_transformer.py
| Description : A sklearn.feature_extraction.text type class for computing PMI from a count matrix.
| Author      : Pushpendre Rastogi
| Created     : Sun Dec  4 23:24:26 2016 (-0500)
| Last-Updated: Wed Dec  7 16:14:42 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 5
'''
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import scipy as sp
NINF=-np.inf

class PmiTransformer(BaseEstimator, TransformerMixin):
    '''
    prepmi-threshold = Chop off low frequency counts altogether.
    ## Vanilla PMI
    PMI = log(P(w,c)/P(w)P(c))
    PPMI = max(PMI, 0)
    Shifted-PPMI = max(PMI, thresh)
    #### Smooth the probability distribution used in PMI.
    ## Power Smoothing
    # P_α(c) = count(c)^α / sum(count(c)^α)
    Discounted-PMI = P(w,c)/P(w)P_α(c)
    Discounted-PPMI = max(Discounted-PMI, 0)
    Shifted-Discounted-PPMI = max(Discounted-PMI, thresh)

    ## Laplace Smoothing
    # P_β(c) = (count(c)+β)/(sum(count(c)) + |C| β)
    Laplace-PMI
    Laplace-PPMI
    Shifted-Discounted-PPMI
    '''
    def __init__(self):
        pass

    def fit(self, X, y=None):
        """
        X : sparse matrix, [n_samples, n_features]
            a matrix of term/token counts
        """
        if not sp.issparse(X):
            X = sp.csc_matrix(X)

        return self

    def transform(self, X, copy=False):
        """
        X : sparse matrix, [n_samples, n_features]
            a matrix of term/token counts
        copy : boolean, default False
        --- OUTPUT ---
        vectors : sparse matrix, [n_samples, n_features]
        """
        if hasattr(X, 'dtype') and np.issubdtype(X.dtype, np.float):
            # preserve float family dtype
            X = sp.csr_matrix(X, copy=copy)
        else:
            # convert counts or binary occurrences to floats
            X = sp.csr_matrix(X, dtype=np.float64, copy=copy)
        n_samples, n_features = X.shape

        return X
