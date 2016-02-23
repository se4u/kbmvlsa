#!/usr/bin/env python
'''
| Filename    : compare_vn_strategy_on_us_presidents.py
| Description : Compare MAD, VN, RESCAL on the US Presidents Dataset.
| Author      : Pushpendre Rastogi
| Created     : Mon Feb 22 12:11:33 2016 (-0500)
| Last-Updated: Tue Feb 23 01:45:39 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 99
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
from collections import defaultdict

vicePresident = rdflib.term.URIRef(
    u'http://dbpedia.org/ontology/vicePresident')
president = rdflib.term.URIRef(u'http://dbpedia.org/ontology/president')
party = rdflib.term.URIRef(u'http://dbpedia.org/ontology/party')
r2idx = {vicePresident: 0, president: 1, party: 2}


def calc_metric(yhat, ygold):
    ''' Nickle ranked all parties by their entries in the reconstructed
    party-membership-slice and recorded the area under the precision-recall curve
    '''
    aupr = 0.0
    p_at_k = defaultdict(float)
    for pred, truth in zip(yhat, ygold):
        sorted_pred_truth = sorted(
            zip(pred, truth), key=lambda x: x[0], reverse=True)
        relevance = [e[1] for e in sorted_pred_truth]
        assert len(relevance) == 14
        aupr += rasengan.rank_metrics.average_precision(
            relevance)
        for k in args.p_at_k:
            p_at_k[k] += rasengan.rank_metrics.precision_at_k(relevance, k)
    return [aupr / yhat.shape[0]] + [p_at_k[k] / yhat.shape[0] for k in args.p_at_k]


def rescal_perf(T, test_node_idx, people_list):
    T_train = np.copy(T)
    T_train[test_node_idx, :, 2] = 0
    T_pred = predict_rescal_als(
        [lil_matrix(T_train[:, :, i]) for i in range(3)],
        rank=args.rank, lambda_A=args.lambda_A, lambda_R=args.lambda_R)
    return calc_metric(
        T_pred[test_node_idx, len(people_list):, 2],
        T[test_node_idx, len(people_list):, 2])


def main():
    g = rdflib.Graph()
    g.parse(config.us_president_fn, format="xml")
    g = list(iter(g))
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
        T[node_set[e1], node_set[e2], r2idx[r]] = 1
        if r2idx[r] == 2:
            assert node_set[e2] >= len(people_list)
    assert T.shape == (93, 93, 3)
    metrics = defaultdict(list)
    for train_node_idx, test_node_idx in rasengan.crossval(len(people_list), 10):
        metrics["RESCAL"].append(rescal_perf(T, test_node_idx, people_list))
        metrics["MAD"].append(
            mad_perf(g, node_set, train_node_idx,
                     range(len(people_list), len(people_list) + len(party_list))))
        metrics["VN"].append(vn_perf(
            np.maximum(T[:, :, 0], T[:, :, 1].T),
            T[:, len(people_list):, 2],
            train_node_idx,
            test_node_idx))
    print metrics
    for algo in ["RESCAL", "VN", "MAD"]:
        print "%s & " % algo, \
            ' & '.join('%.2f' % e for e in np.array(metrics[algo]).mean(axis=0)), \
            r"\\"


def embed_graph_adjacency(adj_mat):
    node_strength = adj_mat.sum(axis=1).astype('float64')
    D = np.diag(node_strength / adj_mat.shape[0])
    return np.linalg.svd(adj_mat + D, full_matrices=0)


def transform_train_features_train_labels(train_features, train_labels):
    f_list = []
    l_list = []
    for f, l in zip(train_features, train_labels):
        for idx in l.nonzero()[0]:
            f_list.append(f)
            l_list.append(idx)
            rasengan.warn("We are breaking")
            break
    f_list = np.array(f_list)
    l_list = np.array(l_list)
    return (f_list, l_list)


def vn_perf(adj_mat, label_mat, train_node_idx, test_node_idx, dim=50):
    ''' The method is to first embed the graph.
    then to train a logistic classifier using the train_node_idx.
    Then test it on the test_node_idx.
    '''
    from sklearn.linear_model import LogisticRegression
    A_svd = embed_graph_adjacency(adj_mat)
    V = A_svd[2].T
    vertex_features = V[:, :dim] * np.sqrt(A_svd[1][:dim])
    train_labels = label_mat[train_node_idx]
    train_features = vertex_features[train_node_idx]
    test_labels = label_mat[test_node_idx]
    test_features = vertex_features[test_node_idx]
    model = LogisticRegression(
        penalty='l2', solver='liblinear', verbose=0)
    train_features, train_labels = transform_train_features_train_labels(
        train_features, train_labels)
    model.fit(train_features, train_labels)
    # Training Score.
    # model.score(train_features, train_labels)
    test_features, test_labels = transform_train_features_train_labels(
        test_features, test_labels)
    # ("Currently there is a problem that the vertex nomination code does"
    #  " not gracefully handle multilabels. What would be the right way to"
    #  " handle it?")
    return [model.score(test_features, test_labels)]


def get_edgelist(g, node_set):
    edgelist = []
    for (e1, r, e2) in g:
        # Edges always go from vicePresident to president.
        if r == vicePresident:
            edgelist.append((node_set[e1], node_set[e2]))
        elif r == president:
            edgelist.append((node_set[e2], node_set[e1]))
        else:
            pass
    edgelist = list(set(edgelist))
    return edgelist


def mad_perf(g, node_set, train_node_idx, label_list):
    edgelist = get_edgelist(g, node_set)
    from evaluate_mad_on_sbm_graph import MAD
    madobj = MAD(edgelist)
    train_data = defaultdict(list)
    test_data = defaultdict(list)
    for (e1, r, e2) in g:
        if r == party:
            if node_set[e1] in train_node_idx:
                train_data[node_set[e2]].append(node_set[e1])
            else:
                test_data[node_set[e2]].append(node_set[e1])
    test_data = dict(test_data)
    train_data = dict(train_data)
    madobj.write_train(train_data)
    madobj.write_test(test_data)
    madobj.execute()
    node_rating = madobj.parse_ratings()
    aupr = 0.0
    p_at_k = defaultdict(float)
    for node, label_rating in node_rating.items():
        sorted_label_rating = []
        for e, _ in sorted(label_rating.items(), key=lambda x: x[1], reverse=True):
            if e != '__DUMMY__':
                sorted_label_rating.append(int(e[1:]))
        remaining_labels = [
            e for e in label_list if e not in sorted_label_rating]
        random.shuffle(remaining_labels)
        relevance = [(1 if (e in test_data and node in test_data[e]) else 0)
                     for e in sorted_label_rating + remaining_labels]
        aupr += rasengan.rank_metrics.average_precision(relevance)
        for k in args.p_at_k:
            p_at_k[k] += rasengan.rank_metrics.precision_at_k(relevance, k)

    return [aupr / len(node_rating)] + [p_at_k[k] / len(node_rating) for k in args.p_at_k]

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--rank', default=5, type=int, help='Default={90}')
    arg_parser.add_argument(
        '--lambda_A', default=.1, type=float, help='Default={10}')
    arg_parser.add_argument(
        '--lambda_R', default=.1, type=float, help='Default={10}')
    arg_parser.add_argument(
        '--p_at_k', default=(1, 5, 10), type=tuple, help='Default={(1, 5, 10)}')
    args = arg_parser.parse_args()
    import random
    random.seed(args.seed)
    np.random.seed(args.seed)
    import ipdb as pdb
    import traceback
    import sys
    import signal
    signal.signal(signal.SIGUSR1, lambda _sig, _frame: pdb.set_trace())
    try:
        main()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

# Local Variables:
# eval: (progn (company-mode -1) (anaconda-mode -1) (eldoc-mode -1))
# eval: (progn (hs-minor-mode -1) (orgtbl-mode -1))
# End:
