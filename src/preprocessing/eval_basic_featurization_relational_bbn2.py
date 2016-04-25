#!/usr/bin/env python
'''
| Filename    : eval_basic_featurization_relational_bbn2.py
| Description : Evaluate the basic featurization based method.
| Author      : Pushpendre Rastogi
| Created     : Sun Apr 17 23:47:08 2016 (-0400)
| Last-Updated: Fri Apr 22 09:00:10 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 218
'''
import random
import numpy as np
random.seed(0)
np.random.seed(0)
import yaml
import rasengan
import cPickle as pkl
from scipy.sparse import csc_matrix
from sklearn.linear_model import SGDClassifier
from rasengan import rank_metrics
import scipy
import numpy
from functools import wraps
import re
import itertools
from collections import defaultdict


rasengan.DISABLE_TICTOC = True
VERBOSE = False
LOAD_DATA = True
IDX_PKL_FN = r'../../scratch/relational_bbn2_train_test_idx.pkl'
USE_SMALL_TEST_SET = False


class DatasetTooSmall(Exception):
    pass


class Dataset(object):

    def __init__(self, featrow_names, feat, positive_idx, negative_idx, idx2feat_map, perma_mask=None, test_size_by2=25):
        assert len(positive_idx) + len(negative_idx) == feat.shape[0]
        self.featrow_names = featrow_names
        self.feat = feat
        self.columns = feat.shape[1]
        self.rows = feat.shape[0]
        self.idx2feat_map = idx2feat_map
        random.shuffle(positive_idx)
        random.shuffle(negative_idx)
        self.positive_idx = positive_idx
        self.positive_idx_set = set(positive_idx)
        self.negative_idx = negative_idx
        # Fix the test set !! Do not work with varying test sets !!
        self.test_size_by2 = test_size_by2
        if test_size_by2 > len(positive_idx) or test_size_by2 > len(negative_idx):
            raise DatasetTooSmall
        self.perma_mask = ([] if perma_mask is None else perma_mask)
        self.mask = []
        return

    def get_row_features(self, row_idx):
        tmp = scipy.sparse.find(self.feat[row_idx])
        return ([self.idx2feat_map[e] for e in tmp[1]], tmp[2])

    def col_idx_to_keep(self):
        mask = set(self.mask + self.perma_mask)
        return [e for e in range(self.columns) if e not in mask]

    def get_max_size(self):
        max_positive_size = len(self.positive_idx) - self.test_size_by2
        max_negative_size = len(self.negative_idx) - self.test_size_by2
        max_size = min(max_positive_size, max_negative_size)
        return max_size

    def get_half_size(self, half_size):
        max_size = self.get_max_size()
        if half_size is None:
            half_size = max_size
        else:
            if half_size > max_size:
                raise DatasetTooSmall
        return half_size

    def get_train_set_idx(self, half_size):
        return self.positive_idx[:half_size] + self.negative_idx[:half_size]

    def get_train_set(self, half_size=None, train_idx=None):
        half_size = self.get_half_size(half_size)
        train_idx = (self.get_train_set_idx(half_size)
                     if train_idx is None
                     else train_idx)
        feat_rows = self.feat[train_idx]
        assert len(train_idx) == 2 * half_size
        return (feat_rows[:, self.col_idx_to_keep()],
                [1] * half_size + [-1] * half_size)

    def get_train_set_names(self, half_size=None, train_idx=None):
        half_size = self.get_half_size(half_size)
        train_idx = (self.get_train_set_idx(half_size)
                     if train_idx is None
                     else train_idx)
        assert len(train_idx) == 2 * half_size
        return ([self.featrow_names[e] for e in train_idx],
                train_idx,
                [1] * half_size + [-1] * half_size)

    def get_test_set_idx(self):
        return (self.positive_idx[- self.test_size_by2:]
                + self.negative_idx[- self.test_size_by2:])

    def get_test_set(self, test_idx=None):
        test_idx = (self.get_test_set_idx()
                    if test_idx is None
                    else test_idx)
        feat_rows = self.feat[test_idx]
        return (feat_rows[:, self.col_idx_to_keep()],
                [1 if i in self.positive_idx_set else -1 for i in test_idx])

    def get_test_set_names(self, test_idx=None):
        test_idx = (self.get_test_set_idx()
                    if test_idx is None
                    else test_idx)
        return ([self.featrow_names[e] for e in test_idx],
                test_idx,
                [1 if i in self.positive_idx_set else -1 for i in test_idx])

    def mask_col(self, pattern=None, mask_inverse=False):
        mask = ([e
                 for e in range(self.columns)
                 if pattern.match(self.idx2feat_map[e])]
                if pattern is not None
                else self.mask)
        self.mask = ([not e for e in mask]
                     if mask_inverse
                     else mask)
        return

    def interpret_coef(self, coef):
        return zip((self.idx2feat_map[e] for e in self.col_idx_to_keep()),
                   coef)

    def max_coef(self, coef):
        ic = self.interpret_coef(coef)
        return max(ic, key=lambda x: x[1])

    def min_coef(self, coef):
        ic = self.interpret_coef(coef)
        return min(ic, key=lambda x: x[1])


def binary_linear_classifier_diagnostics(
        ds,
        train_size_by2=5,
        mask_pattern=re.compile('~document~.*'),
        train_idx=None,
        test_idx=None):
    ds.mask_col(pattern=mask_pattern)
    try:
        train_set = ds.get_train_set(train_size_by2, train_idx=train_idx)
    except DatasetTooSmall:
        print 'Train Set too Big'
        return
    cls = SGDClassifier(loss='hinge',
                        penalty='l2',
                        learning_rate='optimal',
                        average=10,
                        warm_start=False,
                        class_weight='balanced').fit(*train_set)
    # cls = SGDClassifier().fit(*train_set)
    test_feat, test_label = ds.get_test_set(test_idx=test_idx)
    for coef_ in [np.array([[e if e > 0 else 0 for e in cls.coef_.squeeze()]]),
                  # cls.coef_
                  ]:
        cls.coef_ = coef_
        if VERBOSE:
            tmp = ds.get_test_set_names(test_idx=test_idx)
            print zip(*tmp)
            for e in zip(tmp[0], tmp[2], [zip(*ds.get_row_features(e)) for e in tmp[1]]):
                print e
        tmp = zip(test_label, cls.decision_function(test_feat))
        random.shuffle(tmp)
        _y_pred, _ = zip(*sorted(tmp, key=lambda x: x[1], reverse=True))
        _y_pred_randombaseline = zip(*tmp)[0]
        y_pred = [(1 if e > 0 else 0) for e in _y_pred]
        y_pred_randombaseline = [(1 if e > 0 else 0)
                                 for e in _y_pred_randombaseline]
        # 'average=', average, \
        print 'Criteria=%s' % ds.idx2feat_map[ds.perma_mask[0]], \
            'train_rows=%d' % train_set[0].shape[0], \
            'mask_pattern.pattern=%s' % mask_pattern.pattern, \
            'train_col=%d' % train_set[0].shape[1],

        for k in itertools.takewhile(lambda x: x <= 2 * ds.test_size_by2, [10, 100]):
            print 'P@%d=%.4f' % (k, rasengan.rank_metrics.precision_at_k(y_pred, k)),
            print 'BASE-P@%d=%.4f' % (k, rasengan.rank_metrics.precision_at_k(y_pred_randombaseline, k)),
        print 'AUPR=%.3f' % rasengan.rank_metrics.average_precision(y_pred),
        print 'BASE-AUPR=%.3f' % rasengan.rank_metrics.average_precision(y_pred_randombaseline)
        # print ds.max_coef(cls.coef_.squeeze())
        # print ds.min_coef(cls.coef_.squeeze())
        if VERBOSE:
            for e in sorted(ds.interpret_coef(cls.coef_.squeeze()), key=lambda x: x[1], reverse=True)[:10]:
                print '\t', e
            tmp = ds.get_train_set_names(train_size_by2, train_idx=train_idx)
            print zip(*tmp)
            for e in zip(tmp[0], tmp[2], [zip(*ds.get_row_features(e)) for e in tmp[1]]):
                print e
    # import ipdb as pdb
    # pdb.set_trace()
    # print FTI.sort(descending=True, compose=None)[:3]
    # print FTI.sort(descending=False, compose=None)[:3]
    # print FTI.sort(coef=np.asarray(ds.test_set[0][0].todense()).squeeze(),
    #                compose=None)[:10]
    return


def main():
    with rasengan.tictoc('Yaml Loading'):
        cfg = rasengan.deep_namespacer(
            yaml.load(open('relationalize_base_graph.yaml')))
    feat_strings = []
    for k in (_
              for _ in cfg.features
              if _ not in ['adept-core#ChargeIndict', 'adept-core#BeBorn']):
        v = [e for e in cfg.features[k].keys()
             if e not in ['person', 'document', 'confidence']]
        for e in v:
            feat_strings.append(k + '~' + e + '~name~')
    fn = ('/Users/pushpendrerastogi/data/'
          'tackbp2015bbn2/basicfeaturization_relational_bbn2.pkl')
    data = pkl.load(open(fn))
    vertex_dict = data['vertex_dict']
    edgelist = data['edgelist']
    TOTAL_FEATURES = data['TOTAL_FEATURES']
    F2I_MAP = data['PERFECT_HASH']
    I2F_MAP = dict((a, b) for (b, a) in F2I_MAP.iteritems())
    TOTAL_PERSONS = len(vertex_dict)
    with rasengan.tictoc('docs creation'):
        docs = set([fs['~document'] for v in vertex_dict.values()
                    for fs in v.featsets])

    with rasengan.tictoc('s_features creation'):
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

        s_features = csc_matrix(
            (data, (row, col)), shape=[len(vertex_dict), TOTAL_FEATURES])

    feature_occurrence = lambda rpfx: [(e, v, s_features[:, v].getnnz(), s_features[:, v].sum())
                                       for e, v
                                       in F2I_MAP.items()
                                       if e.startswith(rpfx)]

    high_occurrence_feat = lambda rpfx: sorted(
        [e for e in feature_occurrence(rpfx) if e[2] > 1],
        key=lambda x: x[2], reverse=True)
    # adept-core#Origin~origin~name~"Israel"
    # adept-core#Resident~location~name~"United States"
    # adept-core#Die~pod~name~"Iraq"
    # adept-core#Die~pod~name~"United States"
    # adept-core#Die~pod~name~"Pakistan"
    # adept-core#Leadership~subject_org~name~"Democrats"
    # adept-core#StudentAlum~almamater~name~"Harvard University"
    # adept-core#InvestorShareholder~invested_org~name~"Chrysler"
    # adept-core#InvestorShareholder~invested_org~name~"Boston Globe"
    # adept-core#InvestorShareholder~invested_org~name~"New York Post"
    # adept-core#EmploymentMembership~employer~name~"United States"
    # adept-core#Role~role~name~"manager"
    # adept-core#Founder~founded_org~name~"Church"
    # adept-core#Founder~founded_org~name~"Solamere Capital"
    # adept-core#Founder~founded_org~name~"Tesla Motors"
    # We used the high_occurrence_feat function to find out the right
    # features to use.
    if LOAD_DATA:
        data_used = pkl.load(open(IDX_PKL_FN, 'rb'))
    else:
        data_used = defaultdict(dict)
    for feat in [
            'adept-core#EmploymentMembership~employer~name~"Army"',
            'adept-core#EmploymentMembership~employer~name~"White House"',
            'adept-core#Leadership~subject_org~name~"Democratic"',
            'adept-core#Leadership~subject_org~name~"Parliament"',
            'adept-core#Origin~origin~name~"American"',
            'adept-core#Origin~origin~name~"Russia"',
            'adept-core#Resident~location~name~"Chinese"',
            'adept-core#Resident~location~name~"Texas"',
            'adept-core#Role~role~name~"author"',
            'adept-core#Role~role~name~"director"',
            'adept-core#StudentAlum~almamater~name~"Harvard"',
            'adept-core#StudentAlum~almamater~name~"Stanford"']:
        feat_idx = F2I_MAP[feat]
        I = list(s_features[:, feat_idx].nonzero()[0])
        sI = set(I)
        Ic = list(
            [_ for _ in range(s_features.shape[0]) if _ not in sI])
        random.shuffle(I)
        random.shuffle(Ic)

        # preamble = '\npfx=%s feature_rank=%d feat=%s' % (
        #     pfx, feature_rank, feat)
        for trials in range(5):
            preamble = 'feat=%s' % feat
            try:
                if len(I) < 10:
                    raise DatasetTooSmall
                ds = Dataset(
                    row_names, s_features, I, Ic, I2F_MAP, perma_mask=[feat_idx], test_size_by2=min(25, len(I) / 2))
                if not LOAD_DATA:
                    data_used[feat][trials] = dict(train=ds.get_train_set_idx(5),
                                                   test=ds.get_test_set_idx())
                assert feat_idx not in ds.col_idx_to_keep()
            except DatasetTooSmall:
                print preamble, '\nTest Set too big'
                continue
            if not LOAD_DATA:
                continue
            for train_size_by2 in [5]:  # (2, 5, 10, 20):
                for mask_pattern in (re.compile('~document~.*'), re.compile('XXXX')):
                    print preamble, 'train_size_by2=%d' % train_size_by2, \
                        'mask_pattern.pattern=%s' % mask_pattern.pattern
                    train_idx = (
                        data_used[feat][trials]['train'] if LOAD_DATA else None)
                    if USE_SMALL_TEST_SET:
                        test_idx = (
                            data_used[feat][trials]['test'] if LOAD_DATA else None)
                    else:
                        set_train_idx = set(train_idx)
                        test_idx = ([i for i in range(TOTAL_PERSONS) if i not in set_train_idx]
                                    if LOAD_DATA
                                    else None)
                    binary_linear_classifier_diagnostics(
                        ds,
                        train_size_by2=train_size_by2,
                        mask_pattern=mask_pattern,
                        train_idx=train_idx,
                        test_idx=test_idx)
    # The feature runs are over.
    if not LOAD_DATA:
        with open(IDX_PKL_FN, 'wb') as f:
            pkl.dump(dict(data_used), f, protocol=-1)

if __name__ == '__main__':
    main()
#  Local Variables:
#  eval: (progn (linum-mode 1) (eldoc-mode -1) (company-mode -1))
#  End:
