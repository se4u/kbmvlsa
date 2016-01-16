#!/usr/bin/env python
'''
| Filename    : random_walk_on_optimized_datastructure.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Fri Jan 15 19:38:03 2016 (-0500)
| Last-Updated: Fri Jan 15 20:17:35 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 17
'''
from random_walk_on_igraph import read_queries, weighted_random_walk, initial_args
import rasengan
import config
import os
import cPickle as pickle
import numpy as np
from map_flatfileids_in_query_file_to_igraph_format import read_flatfile_query_fn

def main():
    with open(args.graph_fn) as f:
        data = pickle.load(f)
        pass
    adjacent_node_dict = data['graph']
    edge_prob_dict = data['graph_weights']
    for vertex in edge_prob_dict:
        s = edge_prob_dict[vertex].sum()
        edge_prob_dict[vertex] = edge_prob_dict[vertex] / s
    queries = read_flatfile_query_fn(args.query_fn)
    vertex_count = len(adjacent_node_dict)
    query_visit = {}
    with rasengan.tictoc("Random Walks"):
        for qid, query in queries.iteritems():
            for start in query:
                start = int(start)
                query_visit[qid, start] = weighted_random_walk(
                    vertex_count,
                    start,
                    adjacent_node_dict,
                    edge_prob_dict,
                    path_maxlength=args.path_maxlength,
                    n_runs=args.n_runs)
    with open(args.out_fn, 'wb') as ofh:
        pickle.dump(query_visit, ofh)
    return

if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=1234, type=int)
    arg_parser.add_argument('--path_maxlength', default=10, type=int)
    arg_parser.add_argument('--n_runs', default=10, type=int)
    arg_parser.add_argument(
        '--graph_fn', default=config.optimal4randomwalk_enron_contactgraph_fn,
        type=str)
    arg_parser.add_argument(
        '--query_fn', default=config.flat_enron_query_fn, type=str)
    arg_parser.add_argument('--out_fn', default='tmp.pickle', type=str)
    args=arg_parser.parse_args()
    import random
    random.seed(args.seed)
    np.random.seed(args.seed)
    print args
    with rasengan.debug_support():
        main()
