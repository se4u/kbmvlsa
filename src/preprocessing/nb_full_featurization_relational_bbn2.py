#!/usr/bin/env python
'''
| Filename    : nb_full_featurization_relational_bbn2.py
| Description : Perform Naive Bayes based vertex ranking.
| Author      : Pushpendre Rastogi
| Created     : Sat Apr 23 20:26:27 2016 (-0400)
| Last-Updated: Sun Apr 24 10:09:20 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 42
'''
import random
import numpy as np
random.seed(0)
np.random.seed(0)
import cPickle as pkl
from scipy.sparse import csr_matrix, csc_matrix
import scipy
import rasengan
import subprocess
import collections
from rasengan import rank_metrics
from sklearn.naive_bayes import BernoulliNB

IDX_PKL_FN = r'../../scratch/relational_bbn2_train_test_idx.pkl'
fn = ('/Users/pushpendrerastogi/data/'
      'tackbp2015bbn2/basicfeaturization_relational_bbn2.pkl')
data = pkl.load(open(fn))
vertex_dict = data['vertex_dict']
edgelist = data['edgelist']
TOTAL_FEATURES = data['TOTAL_FEATURES']
F2I_MAP = data['PERFECT_HASH']
I2F_MAP = dict((a, b) for (b, a) in F2I_MAP.iteritems())
guid_list = vertex_dict.keys()
vertices = [vertex_dict[e] for e in guid_list]
features = [v.features for v in vertices]
row_names = [v.name for v in vertices]
data = []
row = []
col = []
for r, f in enumerate(features):
    for c, d in f:
        data.append(d)
        col.append(c)
        row.append(r)

total_persons = len(vertex_dict)
docfeat_idx = set(
    [v for e, v in F2I_MAP.iteritems() if e.startswith('~document~')])
s_features = csc_matrix(
    (data, (row, col)), shape=[total_persons, TOTAL_FEATURES])

# ----------------------- #
# Create Backoff Features #
# ----------------------- #


def get_backoff_feature_name(_f):
    return _f.split('~')[-1]

backoff_featdict = collections.defaultdict(list)
for (f, i) in F2I_MAP.iteritems():
    if 'adept-core' in f:
        backoff_featdict[get_backoff_feature_name(f)].append(i)

# Show the histogram of counts.
# np.unique(sorted(len(e) for e in backoff_featdict.values()), return_counts=True)
backoff_feat_name_to_idx = {}
backoff_col_list = []
for (backoff_feat_idx, (backoff_feat_name, col_list)) in enumerate(
        backoff_featdict.iteritems()):
    assert len(col_list) > 0
    tmp = s_features[:, col_list[0]]
    for i in col_list[1:]:
        tmp = tmp + s_features[:, i]
    backoff_feat_name_to_idx[backoff_feat_name] = backoff_feat_idx
    backoff_col_list.append(tmp)
    pass
s_features_backoff = scipy.sparse.hstack(backoff_col_list)


def get_s_features_backoff(backoff_feat_idx):
    return s_features_backoff[:,
                              [i
                               for i
                               in range(s_features_backoff.shape[1])
                               if i != backoff_feat_idx]]


def get_s_features_nodoc(predicate_idx):
    return s_features[:,
                      [i
                       for i
                       in range(TOTAL_FEATURES)
                       if (i not in docfeat_idx
                           and i != predicate_idx)]]


def get_train_x(featset_name, predicate_name, predicate_idx):
    if featset_name == 's_features_backoff':
        backoff_feat_idx = backoff_feat_name_to_idx[
            get_backoff_feature_name(predicate_name)]
        return get_s_features_backoff(backoff_feat_idx)
    elif featset_name == 's_features_backoff_nodoc':
        backoff_feat_idx = backoff_feat_name_to_idx[
            get_backoff_feature_name(predicate_name)]
        bkoff_part = get_s_features_backoff(backoff_feat_idx)
        nodoc_part = get_s_features_nodoc(predicate_idx)
        return scipy.sparse.hstack([bkoff_part, nodoc_part])
    elif featset_name == 's_features_nodoc':
        return get_s_features_nodoc(predicate_idx)
    elif featset_name == 'random':
        return None
    raise NotImplementedError

if __name__ == '__main__':
    IDX_DATA = pkl.load(open(IDX_PKL_FN))
    for predicate_name in IDX_DATA:
        predicate_idx = F2I_MAP[predicate_name]
        labels = s_features[:, predicate_idx]
        I = list(scipy.sparse.find(labels)[0])
        set_I = set(I)
        for featset_name in ['s_features_nodoc', 's_features_backoff_nodoc',
                             's_features_backoff', 'random']:
            for trials in range(5):
                train_idx = IDX_DATA[predicate_name][trials]['train']
                preamble = 'predicate_name=%s trials=%d featset_name=%s ' % (
                    predicate_name, trials, featset_name)
                cls = BernoulliNB(alpha=1, binarize=0.0, fit_prior=False)

                if featset_name != 'random':
                    train_y = (
                        np.array(labels[train_idx].todense()).squeeze() > 0).astype('int')
                    train_x = get_train_x(
                        featset_name, predicate_name, predicate_idx)
                    cls.fit(train_x[train_idx], train_y)
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
