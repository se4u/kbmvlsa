#!/usr/bin/env python
'''
| Filename    : test_embed.py
| Description : Test the embedding methods
| Author      : Pushpendre Rastogi
| Created     : Mon Jan  2 13:36:07 2017 (-0500)
| Last-Updated: Mon Jan  2 15:31:00 2017 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 33
'''
from lib_embed_entity import Mvlsa, parse
import scipy.sparse.linalg
import scipy.linalg
import numpy as np

def project(M):
    # return M.dot(scipy.sparse.linalg.spsolve(M.T.dot(M), M.T))
    M = M.todense()
    return M.dot(scipy.linalg.solve(M.T.dot(M), M.T))

def full_mvlsa(arrlist):
    # Step 1: Create projection matrices and sum them
    P = sum(project(e) for e in arrlist)
    return scipy.linalg.eigh(P)

def ortho_test(a,b):
    return (np.abs(np.dot(a.T, b)) - np.eye(a.shape[1]))

def test_mvlsa():
    transformer, arguments = parse(
        'Mvlsa@final_dim~100@intermediate_dim~99'
        '@view_transform~IDENTITY@mean_center~0@regularization~0')

    arrlist = [scipy.sparse.rand(m, n, density=0.1, format='csc',
                                 dtype='float32', random_state=rs)
               for rs, (m, n)
               in enumerate([(1000, 100), (1000, 100),
                             (1000, 100), (1000, 100)])]

    eigval, true_emb = full_mvlsa(arrlist)
    true_emb = true_emb[:, -100:]
    transformer = eval(transformer)(**arguments)
    emb = transformer(arrlist)[:, -100:]
    print ortho_test(emb, true_emb)
    import pdb
    pdb.set_trace()
    return

if __name__ == '__main__':
    test_mvlsa()
