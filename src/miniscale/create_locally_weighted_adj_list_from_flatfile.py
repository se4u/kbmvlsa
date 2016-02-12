#!/usr/bin/env python
'''
| Filename    : create_locally_weighted_adj_list_from_flatfile.py
| Description : Since igraph format is too bloated therefore create simpler storage.
| Author      : Pushpendre Rastogi
| Created     : Fri Jan 15 19:06:32 2016 (-0500)
| Last-Updated: Fri Jan 15 19:46:31 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 7
'''
import config
from create_igraph_from_flatfile import read_file
import rasengan
import numpy as np
import collections
import cPickle as pickle
import os

def main():
    with rasengan.tictoc("Reading Data"): # 114s
        data = read_file(args.fn)
        pass

    graph = collections.defaultdict(list)
    graph_weights = collections.defaultdict(list)
    with rasengan.tictoc("Extraction of Graph"): # 28.3s
        for idx, (left_vertex, right_vertex, weight) in enumerate(data):
            if idx % 1000 == 0:
                assert right_vertex not in graph[left_vertex]
                assert left_vertex not in graph[right_vertex]
                print (idx * 100.0) / len(data)
            else:
                pass
            graph[left_vertex].append(right_vertex)
            graph[right_vertex].append(left_vertex)
            graph_weights[left_vertex].append(weight)
            graph_weights[right_vertex].append(weight)

    with rasengan.tictoc("Conversion to np.array"): # 7.3s
        graph = dict(graph)
        graph_weights = dict(graph_weights)
        for vertex in graph:
            graph[vertex] = np.array(graph[vertex])
            graph_weights[vertex] = np.array(graph_weights[vertex])
            pass

    with rasengan.tictoc("Pickling"): # 10.2s
        data = dict(graph=graph, graph_weights=graph_weights)
        with open(args.out_fn, 'wb') as f:
            pickle.dump(data, f, protocol=-1)

if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='Igraph Creator')
    arg_parser.add_argument(
        '--fn', default=config.flat_enron_contactgraph_fn,
        type=str)
    arg_parser.add_argument(
        '--out_fn',
        default=config.optimal4randomwalk_enron_contactgraph_fn,
        type=str)
    args=arg_parser.parse_args()
    main()
