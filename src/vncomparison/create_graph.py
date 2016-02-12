#!/usr/bin/env python
'''
| Filename    : create_graph.py
| Description : A script to sample a graph from an SBM.
| Author      : Pushpendre Rastogi
| Created     : Fri Feb 12 00:10:51 2016 (-0500)
| Last-Updated: Fri Feb 12 02:18:35 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 25
'''
import igraph
import numpy as np
import shelve
import cPickle as pickle
import tempfile


def main():
    block_sizes = [200, 300, 220, 280]
    graph = igraph.GraphBase.SBM(
        sum(block_sizes),
        [[0.70, 0.10, 0.12, 0.05],
         [0.10, 0.80, 0.15, 0.15],
         [0.12, 0.15, 0.75, 0.05],
         [0.05, 0.15, 0.05, 0.85]],
        block_sizes,
        loops=False)
    # Every vertex is assigned to a vertex type according to the given block
    # sizes. Vertices of the same type are assigned conseutive vertex IDs.
    class_to_vertex_id_map = {}
    offset = 0
    for class_id, vertex_count in enumerate(block_sizes):
        vec = range(offset, offset + vertex_count)
        random.shuffle(vec)
        class_to_vertex_id_map[class_id] = vec
        offset += vertex_count

    def data_creator(start, stop):
        return ([(e, 1)
                 for e
                 in (class_to_vertex_id_map[0][start:stop]
                     + class_to_vertex_id_map[2][start:stop])]
                + [(e, 0)
                   for e
                   in (class_to_vertex_id_map[1][start:stop]
                       + class_to_vertex_id_map[3][start:stop])])
    train_data = data_creator(0, 10)
    test_data = data_creator(10, 20)
    print 'train_data', train_data, 'test_data', test_data
    print 'creating shelf:', args.shelf_name
    graph_fn = args.shelf_name + '.graph'
    shelf = shelve.open(args.shelf_name)
    shelf['train_data'] = train_data
    shelf['test_data'] = test_data
    shelf['graph_fn'] = graph_fn
    shelf.close()
    print 'Writing graph to', graph_fn
    graph.write_edgelist(graph_fn)
    return

if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='Shelf an SBM graph')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--shelf_name', default='sbm_seed~0.shelve', type=str)
    args = arg_parser.parse_args()
    import random
    random.seed(args.seed)
    np.random.seed(args.seed)
    main()
