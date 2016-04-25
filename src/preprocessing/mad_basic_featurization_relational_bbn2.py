#!/usr/bin/env python
'''
| Filename    : mad_basic_featurization_relational_bbn2.py
| Description : Perform MAD based Label Propagation for Entity Recommendation
| Author      : Pushpendre Rastogi
| Created     : Thu Apr 21 16:41:11 2016 (-0400)
| Last-Updated: Fri Apr 22 10:57:06 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 76
'''

import random
import numpy as np
random.seed(0)
np.random.seed(0)
import cPickle as pkl
from scipy.sparse import csc_matrix
import scipy
import rasengan
import subprocess
import collections
from rasengan import rank_metrics

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

s_features = csc_matrix(
    (data, (row, col)), shape=[len(vertex_dict), TOTAL_FEATURES])
docfeat_idx = set(
    [v for e, v in F2I_MAP.iteritems() if e.startswith('~document~')])
doc_nodoc = [
    'random',
    'wo_doc',
    'with_doc',
]
total_persons = s_features.shape[0]

# -------------------------------------------------------------------------- #
# Assign a Label to some of the people. This is equivalent to hiding entries #
# -------------------------------------------------------------------------- #
IDX_DATA = pkl.load(open(IDX_PKL_FN))
for feat in IDX_DATA:
    for dnd in doc_nodoc:
        predicate_idx = F2I_MAP[feat]
        labels = s_features[:, predicate_idx]
        for trials in range(5):
            train_idx = IDX_DATA[feat][trials]['train']
            set_train_idx = set(train_idx)
            test_idx = IDX_DATA[feat][trials]['test']
            preamble = 'feat=%s trials=%d dnd=%s ' % (feat, trials, dnd)
            I = list(scipy.sparse.find(labels)[0])
            set_I = set(I)
            if dnd == 'random':
                random.shuffle(test_idx)
                testing_output = [1 if e in I else 0
                                  for e in test_idx]
                print preamble, 'AUPR=%.3f' % rasengan.rank_metrics.average_precision(
                    testing_output),
                testing_output = [(1 if e in set_I else 0)
                                  for e
                                  in range(total_persons)
                                  if e not in set_train_idx]
                sto = sum([e for e in testing_output])
                e0_to = [e for e in testing_output]
                print 'CORRECTAUPR=%.3f' % rasengan.rank_metrics.average_precision(
                    e0_to), \
                    'CORRECTP@10=%.3f' % (rasengan.rank_metrics.precision_at_k(
                        e0_to, 10) if sto > 10 else -1), \
                    'CORRECTP@100=%.3f' % (rasengan.rank_metrics.precision_at_k(
                        e0_to, 100) if sto > 100 else -1)
                continue

            with rasengan.tictoc('Writing graph file'):
                with open('graph_file', 'wb') as f:
                    for row, col, val in zip(*scipy.sparse.find(s_features)):
                        if col != predicate_idx and (dnd != 'wo_doc' or col not in docfeat_idx):
                            f.write('%d\t%d\t%.4f\n' %
                                    (row, total_persons + col, val))

            with rasengan.tictoc('Writing Seed File'):
                with open('seed_file', 'wb') as f:
                    for node in train_idx:
                        if node in set_I:
                            f.write('%d\tL1\t1\n' % node)
                        else:
                            f.write('%d\tL0\t1\n' % node)

            output_fn = '../../scratch/%s' % preamble.replace(' ', '')

            with rasengan.tictoc('Junto'):
                status = subprocess.call(
                    "junto config junto_config 1> /tmp/tmp1 2> /tmp/tmp2; mv junto_output '%s'" % output_fn,
                    shell=True)
                status = subprocess.call(
                    '',
                    shell=True)

            output = []
            with open(output_fn, 'rb') as f:
                for row in f:
                    if row.strip() == '':
                        continue
                    node, _1, _2, prediction, _3, _4 = row.strip().split('\t')
                    prediction = prediction.split()
                    tmp = collections.defaultdict(float)
                    for idx in range(0, len(prediction), 2):
                        tmp[prediction[idx]] = float(prediction[idx + 1])
                    output.append(
                        (int(node),
                         float(tmp['L1']),
                         float(tmp['__DUMMY__']),
                         float(tmp['L0'])))

            testing_output = [1 if e[0] in set_I else 0
                              for e
                              in sorted(output, key=lambda x: x[1], reverse=True)
                              if e[0] in test_idx]
            print preamble, 'AUPR=%.3f' % rasengan.rank_metrics.average_precision(
                testing_output),
            testing_output = [([1, e] if e[0] in set_I else [0, e])
                              for e
                              in sorted(output, key=lambda x: x[1], reverse=True)
                              if e[0] < total_persons and e[0] not in train_idx]
            sto = sum([e[0] for e in testing_output])
            e0_to = [e[0] for e in testing_output]
            print 'CORRECTAUPR=%.3f' % rasengan.rank_metrics.average_precision(
                e0_to), \
                'CORRECTP@10=%.3f' % (rasengan.rank_metrics.precision_at_k(
                    e0_to, 10) if sto > 10 else -1), \
                'CORRECTP@100=%.3f' % (rasengan.rank_metrics.precision_at_k(
                    e0_to, 100) if sto > 100 else -1)
