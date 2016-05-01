#!/usr/bin/env python
'''
| Filename    : get_graph_degree.py
| Description : Get the degrees in a graph.
| Author      : Pushpendre Rastogi
| Created     : Sat Apr 30 03:26:44 2016 (-0400)
| Last-Updated: Sat Apr 30 19:39:43 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 18
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
import igraph

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
total_persons = len(vertex_dict)
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
    (data, (row, col)), shape=[total_persons, TOTAL_FEATURES])
docfeat_idx = set(
    [v for e, v in F2I_MAP.iteritems() if e.startswith('~document~')])
docfeat_idx_complement = [
    i for i in range(s_features.shape[1]) if i not in docfeat_idx]

edges, weight = zip(*[[(r, c + total_persons), d]
                      for r, c, d
                      in zip(row, col, data)])

g = igraph.Graph(
    n=total_persons + TOTAL_FEATURES,
    edges=list(edges),
    directed=False).simplify()
cmp = g.components()
set_total_persons = set(range(total_persons))
c, s = np.unique(
    sorted([sum((1 for _ in e if _ in set_total_persons))
            for e in cmp],
           reverse=True),
    return_counts=True)
print c
print s
print sum(_a * _b for _a, _b in zip(c, s))
from sklearn.preprocessing import binarize
degrees = binarize(s_features[:, docfeat_idx_complement]).sum(axis=1)
r, d = np.unique(sorted(degrees, reverse=True), return_counts=True)
print r
print d
print sum(_a * _b for _a, _b in zip(r, d))
total_vertices = 125022
print 'Total vertices', total_vertices
d0v = total_vertices - len(vertex_dict) + d[0]
print 'Number of vertices with 0 degree', d0v, float(d0v) / total_vertices * 20
print 'Number of vertices with 1 degree', d[1], float(d[1]) / total_vertices * 20
print 'Rest of the vertices', sum(d[2:]), float(sum(d[2:])) / total_vertices * 20
