#!/usr/bin/env python
'''
| Filename    : rw_relational_bbn2.py
| Description : Random Walks for Recommendation on Knowledge Graphs.
| Author      : Pushpendre Rastogi
| Created     : Thu Apr 28 07:02:15 2016 (-0400)
| Last-Updated: Thu Apr 28 08:56:33 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 13
'''
import random
import numpy as np
import cPickle as pkl
from scipy.sparse import csc_matrix
import scipy
import rasengan
from collections import Counter
from rasengan import rank_metrics
import os
import ipdb as pdb
import igraph
import argparse
import itertools

arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--seed', default=0, type=int)
arg_parser.add_argument('--rw_walk_num', default=3, type=int)
arg_parser.add_argument('--rw_max_step', default=10, type=int)
args = arg_parser.parse_args()
random.seed(args.seed)
np.random.seed(args.seed)

with rasengan.tictoc('Setup'):
    IDX_PKL_FN = r'../../scratch/relational_bbn2_train_test_idx.pkl'
    fn = os.path.expanduser(
        '~/data/tackbp2015bbn2/basicfeaturization_relational_bbn2.pkl')
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

    global_data = []
    global_row = []
    global_col = []
    for r, f in enumerate(features):
        for c, d in f:
            global_data.append(d)
            global_col.append(c)
            global_row.append(r)

    total_persons = len(vertex_dict)
    docfeat_idx = set(
        [v for e, v in F2I_MAP.iteritems() if e.startswith('~document~')])
    s_features = csc_matrix(
        (global_data, (global_row, global_col)),
        shape=[total_persons, TOTAL_FEATURES])
    IDX_DATA = pkl.load(open(IDX_PKL_FN))
    total_persons_arr = (range(total_persons))
    random.shuffle(total_persons_arr)
    # Till here it only takes 6.2s !!


def get_igraph(feat_idx_to_remove, featset_name):
    assert featset_name in ['s_features_nodoc', 's_features_doc']
    tmp_seq = itertools.izip(global_row, global_col, global_data)
    c_filter = ((lambda c: True)
                if featset_name == 's_features_doc'
                else (lambda c: c not in docfeat_idx))
    edges, weight = zip(*[[(r, c + total_persons), d]
                          for r, c, d
                          in tmp_seq
                          if c != feat_idx_to_remove and c_filter(c)])

    return igraph.Graph(
        n=total_persons + TOTAL_FEATURES,
        edges=list(edges),
        directed=False,
        edge_attrs=dict(weight=list(weight))).simplify()

if __name__ == '__main__':
    for predicate_name in IDX_DATA:
        predicate_idx = F2I_MAP[predicate_name]
        labels = s_features[:, predicate_idx]
        I = list(scipy.sparse.find(labels)[0])
        set_I = set(I)
        for featset_name in [
                's_features_nodoc',
                's_features_doc',
        ]:
            for trials in range(5):
                train_idx = IDX_DATA[predicate_name][trials]['train']
                preamble = 'predicate_name=%s trials=%d featset_name=%s ' % (
                    predicate_name, trials, featset_name)
                g = get_igraph(predicate_idx, featset_name)
                counter = Counter()
                for origin in train_idx:
                    counter.update((e
                                    for e
                                    in rasengan.flatten(
                                        g.random_walk(origin, args.rw_max_step)
                                        for walk_idx
                                        in range(args.rw_walk_num))
                                    if e < total_persons))
                    # pr = g.personalized_pagerank(damping=0.85, reset_vertices=[0])
                    # print len(pr)
                # A large number of vertices are completely left untouched
                # by the random walks, because of their low tendency to discover
                # new things. Imagine a star like graph.
                # Most of the time you'd reach a spoke, and then turn back to
                # the hub. The rate of going from one hub to the other is too
                # low. So
                _testing_output = [[(1 if _i in set_I else 0), _i]
                                   for _i
                                   in itertools.chain(
                                       (i for i, _
                                        in sorted(counter.items(),
                                                  key=lambda x: x[1],
                                                  reverse=True)
                                        if i not in train_idx),
                                       (set(total_persons_arr)
                                        - set(train_idx)
                                        - set(counter.keys())))]
                testing_output = [e[0] for e in _testing_output]
                sto = sum(testing_output)
                print preamble,
                print 'CORRECTAUPR=%.3f' % rasengan.rank_metrics.average_precision(
                    testing_output), \
                    'CORRECTP@10=%.3f' % (rasengan.rank_metrics.precision_at_k(
                        testing_output, 10) if sto > 10 else -1), \
                    'CORRECTP@20=%.3f' % (rasengan.rank_metrics.precision_at_k(
                        testing_output, 20) if sto > 20 else -1)
