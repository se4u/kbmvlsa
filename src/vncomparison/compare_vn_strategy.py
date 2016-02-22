#!/usr/bin/env python
'''
| Filename    : compare_vn_strategy.py
| Description : Compare Three VN Strategies.
| Author      : Pushpendre Rastogi
| Created     : Fri Feb 12 02:19:26 2016 (-0500)
| Last-Updated: Mon Feb 22 06:08:25 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 63
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
from rasengan import rank_metrics


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


def main(graph, VC0_S, VC1_S, block_sizes, **kwargs):
    assert len(block_sizes) == 2
    VC1 = range(block_sizes[0], sum(block_sizes))
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
    nomination_list = sorted(
        enumerate(rating), key=lambda x: x[1], reverse=True)
    training_samples = VC0_S + VC1_S
    nomination_list = filter(
        lambda e: e not in training_samples, nomination_list)
    relevance = [(1.0 if e in VC1 else 0.0)
                 for e, _
                 in nomination_list[:block_sizes[1]]]
    return ["%d" % sum(relevance)] + ["%.1f" % rank_metrics.precision_at_k(relevance, k)
                                      for k in [1, 5, 10, 50]]


def loop_fnc(fnc, block_sizes=(50, 50), training_set_size=20, directed=True,
             seed_list=(0, 1234), loops=False):
    for directed in [True, False]:
        VC1 = range(block_sizes[0], sum(block_sizes))
        assert training_set_size % 2 == 0
        for seed in seed_list:
            random.seed(seed)
            np.random.seed(seed)
            for B_idx, B in enumerate([[[0.55, 0.5], [0.5, 0.55]],
                                       [[0.6, 0.5], [0.5, 0.6]],
                                       [[0.7, 0.5], [0.5, 0.6]]]):
                graph = igraph.GraphBase.SBM(
                    sum(block_sizes), B, list(block_sizes), loops=loops, directed=directed)
                VC0_S = random.sample(
                    xrange(block_sizes[0]), training_set_size / 2)
                VC1_S = random.sample(VC1, training_set_size / 2)
                print ' & '.join(fnc(graph=graph,
                                     VC0_S=VC0_S,
                                     VC1_S=VC1_S,
                                     block_sizes=block_sizes,
                                     seed=seed,
                                     B_idx=B_idx,
                                     B=B)) + r' \\'
            print
    return

if __name__ == '__main__':
    loop_fnc(main)

# Local Variables:
# eval: (progn (company-mode -1) (anaconda-mode -1) (eldoc-mode -1))
# eval: (progn (hs-minor-mode -1) (orgtbl-mode -1))
# End:
