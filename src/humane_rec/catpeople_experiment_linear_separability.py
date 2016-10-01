#!/usr/bin/env python
'''
| Filename    : catpeople_experiment_linear_separability.py
| Description : Test how well can we linearly separate the needles from haystack?
| Author      : Pushpendre Rastogi
| Created     : Wed Sep 28 23:35:41 2016 (-0400)
| Last-Updated: Sat Oct  1 16:05:36 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 95
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
                dual=(needles_in_haystack.shape[0] < len(features)),
                tol=1e-4, fit_intercept=True, verbose=0,
                random_state=args.seed, max_iter=1000)
        else:
            classifier = LinearSVC(
                C=self.expcfg.lsvc_C, intercept_scaling=1000,
                penalty=self.expcfg.lsvc_penalty,
                loss=self.expcfg.lsvc_loss,
                dual=(needles_in_haystack.shape[0] < len(features)),
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
    # with rasengan.debug_support():
    main()


# --------------------------- #
# Without Any Feature Pruning #
# --------------------------- #
'''
In order to figure out the power of the features that we have
we need to use the features that are suggested to us by the training
data and use those features to separate the testing data from noise.

When we run the linear separability experiment using all the features
of the test data, i.e. instead of filtering the features of the test
data we just memorize the test data then we are able to achieve perfect
separation. Of course this result is unsurprising, since we can put
arbitrary weight on unique unigrams from the test documents.
Note that even then the P@10 is only 0.59, which means there are only 6

TODO: This probably suggests a bug, since the train and test performance are
the same all the time.


'''
'''
--Train--
AUPR   0.215
RAUPR  0.000
P@10   0.148
RP@10  0.000
P@100  0.019
RP@100 0.000
MRR    0.264
RMRR   0.001
--Test--
AUPR   0.215
RAUPR  0.000
P@10   0.148
RP@10  0.000
P@100  0.019
RP@100 0.000
MRR    0.264
RMRR   0.000

(Pdb) lsc.pa.limit=1000
--Train--
AUPR   0.283
RAUPR  0.016
P@10   0.191
RP@10  0.015
P@100  0.032
RP@100 0.007
MRR    0.377
RMRR   0.050
--Test--
AUPR   0.285
RAUPR  0.015
P@10   0.195
RP@10  0.009
P@100  0.033
RP@100 0.008
MRR    0.378
RMRR   0.047
'''


# ----------- #
# With DSCTOK #
# ----------- #
'''
Full Results Summary
--Train--
AUPR   0.0078
RAUPR  0.0001
P@10   0.0060
RP@10  0.0000
P@100  0.0013
RP@100 0.0000
MRR    0.0217
RMRR   0.0003
--Test--
AUPR   0.0078
RAUPR  0.0002
P@10   0.0060
RP@10  0.0000
P@100  0.0013
RP@100 0.0002
MRR    0.0217
RMRR   0.0011
Limited Results Summary
--Train--
AUPR   0.0249
RAUPR  0.0054
P@10   0.0190
RP@10  0.0010
P@100  0.0079
RP@100 0.0036
MRR    0.0571
RMRR   0.0093
--Test--
AUPR   0.0264
RAUPR  0.0059
P@10   0.0180
RP@10  0.0030
P@100  0.0077
RP@100 0.0037
MRR    0.0606
RMRR   0.0099
'''
