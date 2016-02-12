#!/usr/bin/env python
'''
| Filename    : random_walk_on_igraph.py
| Description : Perform random walk on igraph which has a weights attribute.
| Author      : Pushpendre Rastogi
| Created     : Fri Jan 15 17:11:21 2016 (-0500)
| Last-Updated: Fri Jan 15 20:07:50 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 16
'''
import igraph
import numpy as np
import rasengan
from collections import defaultdict

def read_queries(query_fn):
    queries = {}
    with rasengan.tictoc("Reading Queries"):
        with open(query_fn) as f:
            for row in f:
                row = row.strip().split()
                qid = row[0]
                queries[qid] = [int(e) for e in row[1:]]
    return queries

def weighted_random_walk(
        vertex_count, start, adjacent_node_list, edge_prob_list,
        path_maxlength=10, n_runs=50):
    assert type(vertex_count) is int
    visit = defaultdict(int)
    for run in range(n_runs):
        state = start
        for steps in range(path_maxlength):
            adjacent_nodes = adjacent_node_list[state]
            edge_probs = edge_prob_list[state]
            state = int(np.random.choice(adjacent_nodes, 1, p=edge_probs))
            visit[state] += 1
            pass
        pass
    return visit

def main():
    with rasengan.tictoc("Loading Graph"):
        graph = igraph.read(args.graph_fn)
        graph.to_undirected(
            mode="collapse", combine_edges=dict(weights="first"))

    with rasengan.tictoc("Creating Adjacent Node List"):
        adjacent_edge_list = graph.get_inclist()
        adjacent_node_list = graph.get_adjlist()

    # 1234 is just a random number.
    assert (adjacent_node_list[1234][0] in
            graph.es[adjacent_edge_list[1234][0]].tuple)

    total_vertices = float(len(adjacent_edge_list))
    with rasengan.tictoc("Creating Local Node Prob List"):
        edge_prob_list = []
        for idx, edges in enumerate(adjacent_edge_list):
            if idx % 1000 == 0:
                print idx / total_vertices  * 100
            weights = np.array(graph.es[edges]["weight"])
            edge_prob_list.append(weights / weights.sum())

    queries = read_queries(args.query_fn)

    for qid, query in queries.iteritems():
        for start in query:
            weighted_random_walk(graph, start, adjacent_node_list,
                                 edge_prob_list,
                                 path_maxlength=args.path_maxlength,
                                 n_runs=args.n_runs)


def initial_args(
        graph_fn="/export/projects/prastogi/kbvn/enron_contactgraph.graphml",
        query_fn="/export/projects/prastogi/kbvn/enron_contactgraph_queries",
        description=''):
    import argparse
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument('--seed', default=1234, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--path_maxlength', default=10, type=int, help='Default={10}')
    arg_parser.add_argument('--n_runs', default=10, type=int, help='Default={10}')
    arg_parser.add_argument('--graph_fn', default=graph_fn, type=str)
    arg_parser.add_argument('--query_fn', default=query_fn, type=str)
    args=arg_parser.parse_args()
    import random
    random.seed(args.seed)
    np.random.seed(args.seed)
    return args

if __name__ == '__main__':
    args = initial_args
    with rasengan.debug_support():
        main()
