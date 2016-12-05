#!/usr/bin/env python
'''
| Filename    : catpeople_experiment_linear_separability.py
| Description : Test how well can we linearly separate the needles from haystack?
| Author      : Pushpendre Rastogi
| Created     : Wed Sep 28 23:35:41 2016 (-0400)
| Last-Updated: Sun Oct  2 03:15:47 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 100
'''
import catpeople_experiment as ce
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
import rasengan
import scipy
import scipy.sparse
from itertools import izip
import util_catpeople as uc
from util_catpeople import index_coo_mat
args = None

class LinSepChecker(ce.ExperimentRunner):
    def __init__(self, *args_, **kwargs):
        super(LinSepChecker, self).__init__(*args_, **kwargs)
        return

    def create_mat_features(self, cat, train_idx):
        mat = (uc.index_coo_mat(self.smat, train_idx, axis=0)
                   if scipy.sparse.isspmatrix_coo(self.smat)
                   else self.smat[train_idx])
        mat = self.keep_only_top_occurring_tokens(mat)
        features = (set(mat.col)
                    if scipy.sparse.isspmatrix_coo(mat)
                    else set(mat.nonzero()[1]))
        return mat, features

    def get_mat_needles_in_haystack(self, features, smat_minus_train):
        mat = (uc.index_coo_mat(self.smat, features, axis=1)
                   if scipy.sparse.isspmatrix_coo(self.smat)
                   else self.smat[:, features])
        needles_in_haystack = (uc.index_coo_mat(mat, smat_minus_train)
                               if scipy.sparse.isspmatrix_coo(mat)
                               else mat[smat_minus_train])
        return mat, needles_in_haystack

    def ls_exp_call_impl(self, fold_idx, cat, train_idx, test_idx):
        mat, features = self.create_mat_features(cat, train_idx)
        print 'Using %d Features For Category %s'%(len(features), cat)
        if len(features) == 0:
            self.pa(cat, [], [], [])
            return
        # ------------------------ #
        # Start Training / Testing #
        # ------------------------ #
        set_train_idx = set(train_idx)
        set_test_idx = set(test_idx)
        features = sorted(features)
        mat, needles_in_haystack = self.get_mat_needles_in_haystack(
            features,
            [i for i in xrange(self.smat.shape[0])
             if (i not in set_train_idx)])
        labels = [(i in set_test_idx)
                  for i in xrange(self.smat.shape[0])
                  if (i not in set_train_idx)]
        if self.expcfg.lsvc_loss == 'logloss':
            classifier = LogisticRegression(
                C=self.expcfg.lsvc_C,
                intercept_scaling=1000,
                penalty=self.expcfg.lsvc_penalty,
                dual=False,
                tol=1e-4, fit_intercept=True, verbose=0,
                random_state=args.seed, max_iter=1000)
        else:
            classifier = LinearSVC(
                C=self.expcfg.lsvc_C, intercept_scaling=1000,
                penalty=self.expcfg.lsvc_penalty,
                loss=self.expcfg.lsvc_loss,
                dual=False,
                tol=1e-4, fit_intercept=True,
                verbose=0, random_state=args.seed, max_iter=1000)
        with rasengan.tictoc('Fitting', timer='total_time'):
            classifier.fit(needles_in_haystack, labels)
        scores = classifier.decision_function(mat)
        # classifier.sparsify()
        self.pa(cat, scores, train_idx, test_idx,
                scratch=dict(
                    coef=classifier.coef_,
                    intercept=classifier.intercept_,
                    features=features))
        return mat, classifier

    def __call__(self):
        for fold_idx, (cat, (train_idx, test_idx)) in enumerate(self.fold_iterator()):
            if self.expcfg.verbose:
                print 'Working on %-4d'%fold_idx, cat,
            self.ls_exp_call_impl(fold_idx, cat, train_idx, test_idx)
        print rasengan.tictoc_timers
        return

def populate_args():
    global args
    args = ce.populate_args()
    ce.args = args
    return args

def main():
    populate_args()
    lsc = LinSepChecker(
        datacfg=ce.DATACONFIG,
        ppcfg=ce.CONFIG[args.ppcfg],
        expcfg=ce.EXPCONFIG[args.expcfg])
    lsc()
    lsc.save_results(fn=args.out_pkl_fn)
    print 'Full Results Summary\n', lsc.pa
    lsc.pa.limit = 1000
    print 'Limited Results Summary\n', lsc.pa

if __name__ == '__main__':
    main()
