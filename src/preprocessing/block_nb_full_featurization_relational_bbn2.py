#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : block_nb_full_featurization_relational_bbn2.py
| Description : Stochastic Block Model inspired Naive Bayes Model
| Author      : Pushpendre Rastogi
| Created     : Sun Apr 24 07:12:14 2016 (-0400)
| Last-Updated: Sun Apr 24 20:42:11 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 79
'''
from sklearn.preprocessing import binarize, LabelBinarizer
import numpy
from itertools import izip
from rasengan import log1mexp
vec_log1mexp = numpy.vectorize(log1mexp)


class BlockNB(object):

    def __init__(self, K_tilde, binarize=0.0, train_iter=3, alpha=1.0, fit_prior=False):
        self.K_tilde = K_tilde
        self.K = -1
        self.binarize = binarize
        self._lcpfl = None  # log_cp_feature_class_given_label
        self.classes_ = 2
        self.pi = None
        self.alpha = alpha
        self.logprob_prior_y = [numpy.log(0.5), numpy.log(0.5)]
        self.train_iter = train_iter
        self._log1mpexp_lcpfl = None
        if fit_prior:
            raise NotImplementedError
        return

    @property
    def classes(self):
        return self.classes_

    @property
    def log1mpexp_lcpfl(self):
        if self._log1mpexp_lcpfl is None:
            self._log1mpexp_lcpfl = vec_log1mexp(self.lcpfl)
        return self._log1mpexp_lcpfl

    @property
    def lcpfl(self):
        return self._lcpfl

    @lcpfl.setter
    def lcpfl(self, val):
        self._log1mpexp_lcpfl = None
        self._lcpfl = val
        return

    def init_fit(self):
        self.lcpfl = numpy.log(numpy.random.rand(self.classes, self.K_tilde))
        self.pi = [-1] * self.K
        return

    def estimate_feature_class(self, X, Y):
        X = X.tocsr()
        lcpfl = self.lcpfl
        log1mpexp_lcpfl = self.log1mpexp_lcpfl
        for k in range(self.K):
            x = np.asarray(X[:, k].todense())
            n_samples = x.shape[0]
            # This loop order is way too slow !!
            # for k_tilde in range(self.K_tilde):
            #     score = 0
            #     lcpfl_slice = self.lcpfl[:, k_tilde]
            #     log1mpexp_lcpfl_slice = log1mpexp_lcpfl[:, k_tilde]
            #     for i in range(n_samples):
            #         if x[i] == 1:
            #             score += lcpfl_slice[Y[i]]
            #         else:
            #             score += log1mpexp_lcpfl_slice[Y[i]]
            #     l[k_tilde]=score
            l = np.zeros(self.K_tilde)
            for i in range(n_samples):
                l += (lcpfl[Y[i], :]
                      if x[i] == 1
                      else log1mpexp_lcpfl[Y[i], :])
            self.pi[k] = np.argmax(l)
        return

    def estimate_conditional_probabilities(self, X, Y):
        ' Count feature values to estimate probabilities. '
        y_size = [[i for i in range(Y.shape[0]) if Y[i] == 0],
                  [i for i in range(Y.shape[0]) if Y[i] == 1]]
        count = np.concatenate(
            [np.array(X[y_size[0]].sum(axis=0)),
             np.array(X[y_size[1]].sum(axis=0))])
        count_fold = numpy.zeros_like(self.lcpfl)
        for k, pi_k in enumerate(self.pi):
            count_fold[:, pi_k] += count[:, k]
        smoothed_fc = count_fold + self.alpha
        denom_arr = numpy.zeros_like(self.lcpfl)
        for y in [0, 1]:
            for k_tilde in range(count_fold.shape[1]):
                denom_arr[y, k_tilde] = (len(y_size[y]) * self.pi.count(k_tilde)
                                         + 2 * self.alpha)
                assert denom_arr[y, k_tilde] >= smoothed_fc[y, k_tilde]
        self.lcpfl = numpy.log(smoothed_fc) - numpy.log(denom_arr)

        return

    def fit(self, X, Y):
        self.K = X.shape[1]
        assert self.K_tilde <= self.K
        X = binarize(X, threshold=self.binarize)
        self.init_fit()
        for _ in range(self.train_iter):
            self.estimate_feature_class(X, Y)
            self.estimate_conditional_probabilities(X, Y)
            print numpy.unique(self.pi, return_counts=True)
        return self

    # def logprob_x_given_y(self, x, p_vec, log1mpexp_p_vec, pi):
    #     assert x.ndim == 1
    #     retval = 0.0
    #     for k in range(len(x)):
    #         retval += (p_vec[pi[k]]
    #                    if x[k] == 1
    #                    else log1mexp_p_vec[pi[k]])
    #     return retval

    # def logprob_y_given_x(self, x):
    #     ' p(y | x) ∝ p(y) p(x | y)'
    #     x = np.asarray(x.todense()).squeeze()
    #     a = self.logprob_x_given_y(x, 1) + self.logprob_prior_y[1]
    #     b = self.logprob_x_given_y(x, 0) + self.logprob_prior_y[0]
    #     c = numpy.logaddexp(a, b)
    #     return [b - c, a - c]

    def predict_log_proba(self, X):
        X = binarize(X, threshold=self.binarize)
        X = X.tocsr()
        retval = []
        pi = self.pi
        p_vec_pi_0 = np.array([self.lcpfl[0][pi[k]]
                               for k in range(X.shape[1])])
        log1mexp_p_vec_pi_0 = np.array([self.log1mpexp_lcpfl[0][pi[k]]
                                        for k in range(X.shape[1])])
        p_vec_pi_1 = np.array([self.lcpfl[1][pi[k]]
                               for k in range(X.shape[1])])
        log1mexp_p_vec_pi_1 = np.array([self.log1mpexp_lcpfl[1][pi[k]]
                                        for k in range(X.shape[1])])
        for i in range(X.shape[0]):
            x = np.asarray(X[i].todense()).squeeze()
            a = (np.where(x, p_vec_pi_1, log1mexp_p_vec_pi_1).sum()
                 + self.logprob_prior_y[1])
            b = (np.where(x, p_vec_pi_0, log1mexp_p_vec_pi_0).sum()
                 + self.logprob_prior_y[0])
            c = numpy.logaddexp(a, b)
            retval.append([b - c, a - c])
        return numpy.array(retval)


from nb_full_featurization_relational_bbn2 import *
IDX_DATA = pkl.load(open(IDX_PKL_FN))


def main(featset_name, predicate_name, trials):
    predicate_idx = F2I_MAP[predicate_name]
    labels = s_features[:, predicate_idx]
    I = list(scipy.sparse.find(labels)[0])
    set_I = set(I)
    train_idx = IDX_DATA[predicate_name][trials]['train']
    preamble = 'predicate_name=%s trials=%d featset_name=%s ' % (
        predicate_name, trials, featset_name)
    cls = BlockNB(10, alpha=1, fit_prior=False)
    if featset_name != 'random':
        train_y = (
            numpy.array(labels[train_idx].todense()).squeeze() > 0).astype('int')
        train_x = get_train_x(
            featset_name, predicate_name, predicate_idx)
        txtdx = train_x[train_idx]
        with rasengan.tictoc('Fitting And Predicting'):
            cls.fit(txtdx, train_y)
            logprob = [(i, e[1])
                       for i, e
                       in enumerate(cls.predict_log_proba(train_x))]
        random.shuffle(logprob)
    else:
        logprob = list(enumerate(np.random.rand(total_persons)))
    testing_output = [1 if i in set_I else 0
                      for i, _
                      in sorted(logprob,
                                key=lambda x: x[1],
                                reverse=True)
                      if i not in train_idx]
    sto = sum(testing_output)
    print preamble,
    print 'CORRECTAUPR=%.3f' % rasengan.rank_metrics.average_precision(
        testing_output), \
        'CORRECTP@10=%.3f' % (rasengan.rank_metrics.precision_at_k(
            testing_output, 10) if sto > 10 else -1), \
        'CORRECTP@100=%.3f' % (rasengan.rank_metrics.precision_at_k(
            testing_output, 100) if sto > 100 else -1)


if __name__ == '__main__':
    from joblib import Parallel, delayed
    Parallel(n_jobs=2)(
        delayed(main)(featset_name, predicate_name, trials)
        for featset_name in ['s_features_nodoc', 's_features_backoff', 'random']
        for predicate_name in IDX_DATA
        for trials in range(5))
