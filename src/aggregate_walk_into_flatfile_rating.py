#!/usr/bin/env python
import rasengan
import config 
import numpy as np
import cPickle as pkl
from collections import defaultdict
from map_flatfileids_in_query_file_to_igraph_format import read_flatfile_query_fn

def main():
    data = pkl.load(open(args.pkl_fn))
    queries = read_flatfile_query_fn(args.query_fn)
    with open(args.out_fn, 'wb') as out_f:
        for qid, query in queries.iteritems():
            agg = defaultdict(int)
            for start in query:
                start = int(start)
                for vertex, visits in data[qid, start].iteritems():
                    if args.agg == 'mean':
                        agg[vertex] = agg[vertex] + float(visits)
                    elif args.agg == 'max':
                        agg[vertex] = max(agg[vertex], float(visits))
                    else:
                        raise NotImplementedError()
            out_f.write(qid)
            for vertex, agg_visits in sorted(agg.items(), 
                                             key=lambda x: x[1], reverse=True):
                out_f.write(' %d=%.2f'%(vertex, agg_visits))
            out_f.write('\n')
    return

if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--pkl_fn', default=r'/export/projects/prastogi/kbvn/enron_contactGraph_seed~1234_length~25_reps~50.pickle', type=str)
    arg_parser.add_argument('--agg', default='mean', type=str)
    arg_parser.add_argument('--out_fn', default='/export/projects/prastogi/kbvn/enron_contactGraph_seed~1234_length~25_reps~50_agg~mean.rating', type=str)
    arg_parser.add_argument(
        '--query_fn', default=config.flat_enron_query_fn, type=str)
    args=arg_parser.parse_args()
    print args
    with rasengan.debug_support():
        main()
