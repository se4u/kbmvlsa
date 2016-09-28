#!/usr/bin/env python
'''
| Filename    : nb_full_featurization_relational_bbn2.py
| Description : Perform Naive Bayes based vertex ranking.
| Author      : Pushpendre Rastogi
| Created     : Sat Apr 23 20:26:27 2016 (-0400)
| Last-Updated: Thu May 12 17:29:11 2016 (+0530)
|           By: Pushpendre Rastogi
|     Update #: 125
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
import os
import ipdb as pdb

IDX_PKL_FN = r'../../scratch/relational_bbn2_train_test_idx.pkl'
fn = os.path.expanduser('~/data/'
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


def index_row_names(idi):
    return [row_names[i] for i in idi]

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
    idx = [i
           for i
           in range(s_features_backoff.shape[1])
           if i != backoff_feat_idx]
    feat_name = [I2F_MAP[i] for i in idx]
    return s_features_backoff[:, idx], feat_name


def get_s_features_doc(predicate_idx):
    idx = [i
           for i
           in range(TOTAL_FEATURES)
           if (i != predicate_idx)]
    feat_name = [I2F_MAP[i] for i in idx]
    return s_features[:, idx], feat_name


def get_s_features_nodoc(predicate_idx):
    idx = [i
           for i
           in range(TOTAL_FEATURES)
           if (i not in docfeat_idx
               and i != predicate_idx)]
    feat_name = [I2F_MAP[i] for i in idx]
    return s_features[:, idx], feat_name


def make_conjunctive_feat(feat, feat_name):
    l = []
    n = []
    base_feat = feat.shape[1]
    assert base_feat == len(feat_name)
    if base_feat > 200:
        rasengan.warn(
            'Making Conjunctive feature with %d base features' % base_feat)
    for i in range(base_feat):
        for j in range(i + 1, base_feat):
            # Maximummeans OR
            l.append(feat[:, i].maximum(feat[:, j]))
            # Minimum means AND
            # l.append(feat[:, i].minimum(feat[:, j]))
            n.append(feat_name[i] + feat_name[j])
    return (scipy.sparse.hstack([feat] + l), feat_name + n)


def get_train_x(featset_name, predicate_name, predicate_idx, train_idx, train_y, use_only_positive_feat=False, create_conjunctive_feat=False):
    if featset_name == 's_features_backoff':
        backoff_feat_idx = backoff_feat_name_to_idx[
            get_backoff_feature_name(predicate_name)]
        train_x, feat_name = get_s_features_backoff(backoff_feat_idx)
    elif featset_name == 's_features_backoff_nodoc':
        backoff_feat_idx = backoff_feat_name_to_idx[
            get_backoff_feature_name(predicate_name)]
        bkoff_part, bkoff_names = get_s_features_backoff(backoff_feat_idx)
        nodoc_part, nodoc_names = get_s_features_nodoc(predicate_idx)
        train_x = scipy.sparse.hstack([bkoff_part, nodoc_part])
        feat_name = (bkoff_names + nodoc_names)
    elif featset_name == 's_features_nodoc':
        train_x, feat_name = get_s_features_nodoc(predicate_idx)
    elif featset_name == 's_features_doc':
        train_x, feat_name = get_s_features_doc(predicate_idx)
    elif featset_name == 'random':
        return None
    # print [feat_name[_] for _ in scipy.sparse.find(train_x[41935])[1]]
    # pdb.set_trace()
    assert train_x.shape[1] == len(feat_name)
    idx_to_use = ([e for e, _ in zip(train_idx, train_y) if _ == 1]
                  if use_only_positive_feat
                  else train_idx)

    non_zero_train_col_set = set(rasengan.flatten(
        scipy.sparse.find(train_x[idx_to_use])[1]))
    non_zero_train_col = list(non_zero_train_col_set)
    train_x = train_x[:, non_zero_train_col]
    feat_name = [feat_name[i] for i in non_zero_train_col_set]
    # print [feat_name[_] for _ in scipy.sparse.find(train_x[41935])[1]]
    # pdb.set_trace()
    assert train_x.shape[1] == len(feat_name)
    if not create_conjunctive_feat:
        return train_x, feat_name
    train_x_2, feat_name_2 = make_conjunctive_feat(train_x, feat_name)
    # print [feat_name[_] for _ in scipy.sparse.find(train_x[41935])[1]]
    # pdb.set_trace()
    return train_x_2, feat_name_2


def my_aupr(l):
    return np.mean([(i + 1) / float(e + 1)
                    for i, e in enumerate(l)])

if __name__ == '__main__':
    IDX_DATA = pkl.load(open(IDX_PKL_FN))
    for predicate_name in IDX_DATA:
        predicate_idx = F2I_MAP[predicate_name]
        labels = s_features[:, predicate_idx]
        I = list(scipy.sparse.find(labels)[0])
        set_I = set(I)
        for featset_name in [
                's_features_nodoc',
                #'s_features_backoff_nodoc',
                #'s_features_backoff',
                #'s_features_doc',
                #'random',
        ]:
            for trials in range(1):  # range(5)
                train_idx = IDX_DATA[predicate_name][trials]['train']
                preamble = 'predicate_name=%s trials=%d featset_name=%s ' % (
                    predicate_name, trials, featset_name)
                cls = BernoulliNB(alpha=1, binarize=0.0, fit_prior=False)

                if featset_name != 'random':
                    train_y = (
                        np.array(labels[train_idx].todense()).squeeze() > 0).astype('int')
                    train_x, feat_name = get_train_x(
                        featset_name, predicate_name, predicate_idx, train_idx, train_y)
                    cls.fit(train_x[train_idx], train_y)
                    logprob = [(i, e[1])
                               for i, e
                               in enumerate(cls.predict_log_proba(train_x))]
                    random.shuffle(logprob)
                else:
                    logprob = list(enumerate(np.random.rand(total_persons)))
                _testing_output = [[(1 if i in set_I else 0), i]
                                   for i, _
                                   in sorted(logprob,
                                             key=lambda x: x[1],
                                             reverse=True)
                                   if i not in train_idx]
                testing_output = [e[0] for e in _testing_output]
                # In order to debug the performance of naive bayes we need to
                # find out the features that were presented at train time.
                # And then the features that the NB classifier rated highly at
                # the test time. The question is that why were the false
                # positives rated so highly?
                print preamble,

                def ftt(feat, feat_name, rownames):
                    retval = {}
                    for i in range(feat.shape[0]):
                        retval[rownames[i]] = [feat_name[e]
                                               for e in scipy.sparse.find(feat[i])[1]]
                    return retval
                import ipdb as pdb
                import traceback
                import sys
                import signal
                from pprint import pprint
                signal.signal(
                    signal.SIGUSR1, lambda _sig, _frame: pdb.set_trace())
                try:
                    rows_at_training_time = index_row_names(train_idx)
                    features_at_training_time = ftt(
                        train_x[train_idx], feat_name, rows_at_training_time)
                    last_r1_i = []
                    for _i, (r, i) in enumerate(_testing_output):
                        if r == 0:
                            if _i > 40:
                                continue
                            tmp = ftt(
                                train_x[i], feat_name, index_row_names([i]))
                            tmp_v = tmp.values()[0]
                            okay_feat = [
                                # 'adept-core#EmploymentMembership~employer~name~"Pentagon"',
                                # 'adept-core#Leadership~subject_org~name~"Army"',
                                # 'adept-core#EmploymentMembership~employer~name~"U.S. Army War College"',
                                # 'adept-core#EmploymentMembership~employer~name~"3rd Armored Cavalry Regiment"',
                            ]
                            if any(e in tmp_v for e in okay_feat):
                                pass
                            else:
                                import ipdb as pdb
                                pdb.set_trace()
                                pprint(_i)
                                pprint(tmp)
                        else:
                            last_r1_i.append([(_i, r, i),
                                              ftt(
                                                  train_x[i],
                                                  feat_name,
                                                  index_row_names([i]))])
                    # pprint(last_r1_i)
                except:
                    type, value, tb = sys.exc_info()
                    traceback.print_exc()
                    pdb.post_mortem(tb)
                sto = sum(testing_output)
                print 'CORRECTAUPR=%.3f' % rasengan.rank_metrics.average_precision(
                    testing_output), \
                    'CORRECTP@10=%.3f' % (rasengan.rank_metrics.precision_at_k(
                        testing_output, 10) if sto > 10 else -1), \
                    'CORRECTP@20=%.3f' % (rasengan.rank_metrics.precision_at_k(
                        testing_output, 20) if sto > 20 else -1), \
                    'TrueAUPR=%.3f' % (my_aupr([e[0][0]
                                                for e
                                                in last_r1_i
                                                if len(e[1].values()[0]) > 0]))
