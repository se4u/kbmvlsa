#!/usr/bin/env python
'''
| Filename    : compare_vn_strategy.py
| Description : Compare Three VN Strategies.
| Author      : Pushpendre Rastogi
| Created     : Fri Feb 12 02:19:26 2016 (-0500)
| Last-Updated: Mon Feb 15 03:03:48 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 24
There are three VN strategies that we want to compare:
1. ASE.
2. VN through KBC.
3. MAD.
4. Modularity.
'''
import igraph
import random
from rescal import rescal_als
import numpy as np
from scipy.sparse import lil_matrix


def predict_rescal_als(T):
    A, R, _, _, _ = rescal_als(
        T, 100, init='nvecs', conv=1e-3,
        lambda_A=10, lambda_R=10
    )
    n = A.shape[0]
    P = np.zeros((n, n, len(R)))
    for k in range(len(R)):
        P[:, :, k] = np.dot(A, np.dot(R[k], A.T))
    return P

block_sizes = [50, 50]
B = [[0.8, 0.2],
     [0.3, 0.7]]
graph = igraph.GraphBase.SBM(sum(block_sizes), B, block_sizes,
                             loops=False, directed=True)
VC0 = range(50)
VC1 = range(51, 100)

training_set_size = 30
assert training_set_size % 2 == 0
VC0_S = random.sample(xrange(50), training_set_size / 2)
VC1_S = random.sample(xrange(51, 100), training_set_size / 2)

# Convert Graph to Adjacency Matrix
adj = np.array(graph.get_adjacency())
V = adj.shape[0]

# Append two rows and columns to the Adjacency Matrix
adj = np.concatenate((adj, np.zeros((2, V))), axis=0)
adj = np.concatenate((adj, np.zeros((V + 2, 2))), axis=1)
# Fill the two rows and columns with data of connection
for idx in VC0_S:
    adj[V, idx] = adj[idx, V] = 1

for idx in VC1_S:
    adj[V + 1, idx] = adj[idx, V + 1] = 1

# Predict unknown values
P = predict_rescal_als([lil_matrix(adj)])

# Use the predicted values.
rating = P[:, V + 1, 0] + P[V + 1, :, 0] - P[:, V, 0] - P[V, :, 0]
nomination_list = sorted(enumerate(rating), key=lambda x: x[1], reverse=True)
# Since C1 is the desirable class.
# Therefore the first 50 elements should lie in range(51,100)
print "The following number should be close to 50.",\
    sum(1 for e, s in nomination_list[:block_sizes[1]] if e in VC1)
import code
vars = globals().copy()
vars.update(locals())
code.InteractiveConsole(locals=vars).interact('')
# Local Variables:
# eval: (progn (company-mode -1) (anaconda-mode -1) (eldoc-mode -1))
# eval: (progn (hs-minor-mode -1) (orgtbl-mode -1))
# End:
