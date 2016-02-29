#!/usr/bin/env python
'''
| Filename    : compare_vn_strategy_on_us_presidents.py
| Description : Compare MAD, VN, RESCAL on the US Presidents Dataset.
| Author      : Pushpendre Rastogi
| Created     : Mon Feb 22 12:11:33 2016 (-0500)
| Last-Updated: Mon Feb 29 03:07:30 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 168
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
    num_slice = T.shape[2]
    T_train[test_node_idx, :, num_slice - 1] = 0
    T_pred = predict_rescal_als(
        [lil_matrix(T_train[:, :, i]) for i in range(num_slice)],
        rank=args.rank, lambda_A=args.lambda_A, lambda_R=args.lambda_R)
    return calc_metric(
        T_pred[test_node_idx, len(people_list):, num_slice - 1],
        T[test_node_idx, len(people_list):, num_slice - 1])


def embed_graph_adjacency(adj_mat, dim):
    node_strength = adj_mat.sum(axis=1).astype('float64')
    D = np.diag(node_strength / adj_mat.shape[0])
    assert not (args.ase_add_diag and args.ase_add_eps2everything)
    if args.ase_add_diag:
        adj_mat = adj_mat + D
    elif args.ase_add_eps2everything:
        adj_mat = adj_mat + args.ase_eps_noise
    else:
        pass
    A_svd = np.linalg.svd(adj_mat, full_matrices=0)
    V = A_svd[2].T
    # print ' '.join('%.2f' % e for e in A_svd[1])
    return V[:, :dim] * np.sqrt(A_svd[1][:dim])


def embed_graph_laplacian(adj_mat, dim):
    node_strength = adj_mat.sum(axis=1).astype('float64')
    D = np.diag(node_strength / adj_mat.shape[0])
    A_svd = np.linalg.svd(np.dot(np.dot(D, adj_mat), D),
                          full_matrices=0)
    if args.ase_add_eps2everything:
        adj_mat = adj_mat + args.ase_eps_noise
    V = A_svd[2].T
    return V[:, :dim]


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


def ase_perf(adj_mat, label_mat, train_node_idx, test_node_idx, dim):
    ''' The method is to first embed the graph.
    then to train a logistic classifier using the train_node_idx.
    Then test it on the test_node_idx.
    '''
    from sklearn.linear_model import LogisticRegression
    if args.ase_embed_adjacency:
        vertex_features = embed_graph_adjacency(adj_mat, dim)
    else:
        vertex_features = embed_graph_laplacian(adj_mat, dim)

    train_labels = label_mat[train_node_idx]
    train_features = vertex_features[train_node_idx]
    test_labels = label_mat[test_node_idx]
    test_features = vertex_features[test_node_idx]
    model = LogisticRegression(
        penalty='l2', solver='liblinear', verbose=0, class_weight='balanced', C=0.1)
    train_features, train_labels = transform_train_features_train_labels(
        train_features, train_labels)
    model.fit(train_features, train_labels)
    # Training Score.
    # model.score(train_features, train_labels)
    test_features, test_labels = transform_train_features_train_labels(
        test_features, test_labels)
    predicted_labels = model.predict(test_features)
    aupr = 0.0
    p_at_k = defaultdict(float)
    for pred_label_idx, label_relevance in zip(predicted_labels, label_mat[test_node_idx]):
        pred_label_relevance = [label_relevance[pred_label_idx]]
        rest_relevance = [label_relevance[idx]
                          for idx in range(len(label_relevance))
                          if idx != pred_label_idx]
        random.shuffle(rest_relevance)
        relevance = pred_label_relevance + rest_relevance
        aupr += rasengan.rank_metrics.average_precision(
            relevance)
        for k in args.p_at_k:
            p_at_k[k] += rasengan.rank_metrics.precision_at_k(relevance, k)
    return [aupr / len(test_node_idx)] + [p_at_k[k] / len(test_node_idx) for k in args.p_at_k]


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


def mad_rating(node_rating, label_list, test_data):
    ''' Node rating maps nodes to label_rating
    label_rating map label_strings to
    Params
    ------
    node_rating :
    label_list  :
    test_data   :
    Returns
    -------
    '''
    aupr = 0.0
    p_at_k = defaultdict(float)
    for node, label_rating in node_rating.items():
        sorted_label_rating = []
        for e, _ in sorted(label_rating.items(), key=lambda x: x[1], reverse=True):
            if e != '__DUMMY__':
                if type(e) is str:
                    sorted_label_rating.append(int(e[1:]))
                else:
                    sorted_label_rating.append(e)
        remaining_labels = [
            e for e in label_list if e not in sorted_label_rating]
        random.shuffle(remaining_labels)
        relevance = [(1 if (e in test_data and node in test_data[e]) else 0)
                     for e in sorted_label_rating + remaining_labels]
        aupr += rasengan.rank_metrics.average_precision(relevance)
        for k in args.p_at_k:
            p_at_k[k] += rasengan.rank_metrics.precision_at_k(relevance, k)

    return [aupr / len(node_rating)] + [p_at_k[k] / len(node_rating) for k in args.p_at_k]


def get_train_test_data(g, node_set, train_node_idx):
    ''' train_data and test_data are maps from vertices to labels.
    '''
    train_data = defaultdict(list)
    test_data = defaultdict(list)
    for (e1, r, e2) in g:
        if r == party:
            if node_set[e1] in train_node_idx:
                train_data[node_set[e2]].append(node_set[e1])
            else:
                test_data[node_set[e2]].append(node_set[e1])
                pass
            pass
        pass
    return dict(train_data), dict(test_data)


def mad_perf(g, node_set, train_node_idx, label_list):
    edgelist = get_edgelist(g, node_set)
    from evaluate_mad_on_sbm_graph import MAD
    madobj = MAD(edgelist)
    train_data, test_data = get_train_test_data(g, node_set, train_node_idx)
    madobj.write_train(train_data)
    madobj.write_test(test_data)
    madobj.execute()
    node_rating = madobj.parse_ratings()
    return mad_rating(node_rating, label_list, test_data)


def random_perf(g, node_set, train_node_idx, label_list):
    _, test_data = get_train_test_data(g, node_set, train_node_idx)
    # -------------------------------------------------------------------- #
    # Figure out how many times does a test president/vicepresident really #
    # has multiple parties/labels? Count this amongst test node in 10 fold #
    # -------------------------------------------------------------------- #
    # node2label = defaultdict(list)
    # for label, nodes in test_data.iteritems():
    #     for node in nodes:
    #         node2label[node].append(label)
    # print "Test Nodes With Multiple Labels", \
    #     sum((len(labels) > 2) for labels in node2label.values())
    node_rating = {}
    for node in rasengan.flatten(test_data.values()):
        node_rating[node] = {}
    return mad_rating(node_rating, label_list, test_data)


def weighted_random_walk(start, adjacent_node_list):
    path_maxlength = args.rw_length
    n_runs = args.rw_repeat
    visit = defaultdict(int)
    for run in range(n_runs):
        state = start
        for steps in range(path_maxlength):
            adjacent_nodes = adjacent_node_list[state]
            # if len(adjacent_nodes) > 0:
            state = int(np.random.choice(adjacent_nodes, 1))
            visit[state] += 1
            pass
        pass
    return visit


def rw_get_label_rating(node, adj_list, vertex_to_label, train_node_idx):
    visit = weighted_random_walk(node, adj_list)
    label_score = defaultdict(float)
    for vertex in visit:
        if vertex in train_node_idx:
            for label in vertex_to_label[vertex]:
                label_score[label] += visit[vertex]
    return dict(label_score)


def randomwalk_perf(adj, labels, train_node_idx,
                    test_data, label_list):
    node_rating = {}
    adj_list = []
    adj = np.maximum(adj, adj.T)
    vertex_to_label = []
    min_label = min(label_list)
    for row in labels:
        vertex_to_label.append(list(row.nonzero()[0] + min_label))
    for row in adj:
        adj_list.append(list(row.nonzero()[0]))
    # --------------------------------------------------------------------------- #
    # For Each query point(test vertex) Create a ranked list of potential labels. #
    # --------------------------------------------------------------------------- #
    for node in rasengan.flatten(test_data.values()):
        node_rating[node] = rw_get_label_rating(
            node, adj_list, vertex_to_label, train_node_idx)
    return mad_rating(node_rating, label_list, test_data)


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
        else:
            assert node_set[e2] < len(people_list)
            assert node_set[e1] < len(people_list)
    assert T.shape == (93, 93, 3)
    RESCAL_T = np.dstack((np.maximum(T[:, :, 0], T[:, :, 1].T), T[:, :, 2]))
    metrics = defaultdict(list)

    '''
    g - A list of RDF triples.
    T - A 93 x 93 x 3 tensor
    train_node_idx - A list of indices of vertices whose labels are known.
    test_node_idx  - A list of indices of vertices whose labels are unknown.
    people_list    - A list of 79 people.
    party_list     - A list of 14 parties.
    Every perf function returns AUPR and P@K for k in args.args.p_at_k
    '''
    label_list = range(len(people_list), len(people_list) + len(party_list))
    for train_node_idx, test_node_idx in rasengan.crossval(len(people_list), 10):
        metrics["RESCAL"].append(
            rescal_perf(T, test_node_idx, people_list))
        metrics["RESCAL_SENSIBLE"].append(
            rescal_perf(RESCAL_T, test_node_idx, people_list))
        metrics["MAD"].append(
            mad_perf(g, node_set, train_node_idx, label_list))
        metrics["ASE"].append(
            ase_perf(np.maximum(T[:, :, 0], T[:, :, 1].T),
                     T[:, len(people_list):, 2],
                     train_node_idx, test_node_idx,
                     args.ase_dim))
        metrics["RANDOM"].append(
            random_perf(g, node_set, train_node_idx, label_list))
        # assert rasengan.flatten(
        #     get_train_test_data(g, node_set, train_node_idx)[1].values()) == test_node_idx
        # It turns out that node 63. actually does not have a party in the
        # database.
        # [ (e1, r, e2) for (e1, r, e2) in g if node_set[e2] == 63]
        # [(rdflib.term.URIRef(u'http://dbpedia.org/resource/Hubert_Humphrey'),
        # rdflib.term.URIRef(u'http://dbpedia.org/ontology/president'),
        # rdflib.term.URIRef(u'http://dbpedia.org/resource/James_Eastland'))]
        metrics["RANDOMWALK"].append(
            randomwalk_perf(
                np.maximum(
                    T[:len(people_list), :len(people_list), 0],
                    T[:len(people_list), :len(people_list), 1].T),  # president
                T[:, len(people_list):, 2],  # Party
                # The people whose labels we use after  walking.
                train_node_idx,
                get_train_test_data(g, node_set, train_node_idx)[1],
                label_list,
            )
        )
    # print metrics
    for algo in ["RESCAL", "RESCAL_SENSIBLE", "ASE", "MAD", "RANDOM", "RANDOMWALK"]:
        print "%s & " % algo, \
            ' & '.join('%.2f' % e for e in np.array(metrics[algo]).mean(axis=0)), \
            r"\\"
    return

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument(
        '--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--rank', default=5, type=int, help='Default={90}')
    arg_parser.add_argument(
        '--lambda_A', default=.1, type=float, help='Default={10}')
    arg_parser.add_argument(
        '--lambda_R', default=.1, type=float, help='Default={10}')
    arg_parser.add_argument(
        '--p_at_k', default=(1, 5, 10), type=tuple, help='Default={(1, 5, 10)}')
    arg_parser.add_argument(
        '--ase_dim', default=50, type=int, help='Default={50}')
    arg_parser.add_argument(
        '--ase_add_diag', default=1, type=int, help='Default={1}')
    arg_parser.add_argument(
        '--ase_add_eps2everything', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--ase_eps_noise', default=1e-2, type=float, help='Default={1e-2}')
    arg_parser.add_argument(
        '--ase_embed_adjacency', default=1, type=int, help='Default={1}')
    arg_parser.add_argument(
        '--rw_length', default=2, type=int, help='Default={2}')
    arg_parser.add_argument(
        '--rw_repeat', default=5, type=int, help='Default={5}')
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
