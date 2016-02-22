#!/usr/bin/env python
'''
| Filename    : compare_vn_strategy_on_us_presidents.py
| Description : Compare MAD, VN, RESCAL on the US Presidents Dataset.
| Author      : Pushpendre Rastogi
| Created     : Mon Feb 22 12:11:33 2016 (-0500)
| Last-Updated: Mon Feb 22 14:53:53 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 44
USAGE: ./compare_vn_strategy_on_us_presidents.py --rank 5 --lambda_A .1 --lambda_R .1
Compare to the performance with `--rank 50 --lambda_A 10 --lambda_R 10`
'''
import rdflib
import config
import numpy as np
import rasengan
from compare_vn_strategy import predict_rescal_als
from scipy.sparse import lil_matrix
import argparse


def calc_metric(yhat, ygold):
    ''' Nickle ranked all parties by their entries in the reconstructed
    party-membership-slice and recorded the area under the precision-recall curve
    '''
    aupr = 0.0
    for pred, truth in zip(yhat, ygold):
        sorted_pred_truth = sorted(
            zip(pred, truth), key=lambda x: x[0], reverse=True)
        aupr += rasengan.rank_metrics.average_precision(
            [e[1] for e in sorted_pred_truth])
    mean_avg_prec = aupr / yhat.shape[0]
    return [mean_avg_prec]


def main():
    g = rdflib.Graph()
    g.parse(config.us_president_fn, format="xml")
    g = list(iter(g))
    vicePresident = rdflib.term.URIRef(
        u'http://dbpedia.org/ontology/vicePresident')
    president = rdflib.term.URIRef(u'http://dbpedia.org/ontology/president')
    party = rdflib.term.URIRef(u'http://dbpedia.org/ontology/party')
    people_list = list(set([e[0] for e in g if e[1] == party]
                           + [e[0] for e in g if e[1] == president]
                           + [e[2] for e in g if e[1] == president]
                           + [e[0] for e in g if e[1] == vicePresident]
                           + [e[2] for e in g if e[1] == vicePresident]))
    party_list = list(set([e[2] for e in g if e[1] == party]))
    assert len(people_list) == 79
    assert len(party_list) == 14
    # Critical to assign lower id to people.
    people_party_list = people_list + party_list
    node_set = dict(
        zip(list(people_party_list), range(len(people_party_list))))
    assert len(node_set) == len(set(node_set))
    # --------------- #
    # Populate Tensor #
    # --------------- #
    T = np.zeros((len(node_set), len(node_set), 3))
    for (e1, r, e2) in g:
        r_idx = (0 if r == vicePresident
                 else (1 if r == president
                       else 2))
        T[node_set[e1], node_set[e2], r_idx] = 1
        if r_idx == 2:
            assert node_set[e2] >= len(people_list)
    assert T.shape == (93, 93, 3)
    metrics = []
    for _, test_node_idx in rasengan.crossval(len(people_list), 10):
        T_train = np.copy(T)
        T_train[test_node_idx, :, 2] = 0
        T_pred = predict_rescal_als(
            [lil_matrix(T_train[:, :, i]) for i in range(3)],
            rank=args.rank, lambda_A=args.lambda_A, lambda_R=args.lambda_R)
        metrics.append(calc_metric(
            T_pred[test_node_idx, len(people_list):, 2],
            T[test_node_idx, len(people_list):, 2]))
    return np.array(metrics).mean(axis=0)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--rank', default=5, type=int, help='Default={90}')
    arg_parser.add_argument(
        '--lambda_A', default=.1, type=float, help='Default={10}')
    arg_parser.add_argument(
        '--lambda_R', default=.1, type=float, help='Default={10}')
    args = arg_parser.parse_args()
    import random
    random.seed(args.seed)
    np.random.seed(args.seed)
    print main()

# Local Variables:
# eval: (progn (company-mode -1) (anaconda-mode -1) (eldoc-mode -1))
# eval: (progn (hs-minor-mode -1) (orgtbl-mode -1))
# End:
