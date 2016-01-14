#!/usr/bin/env python
'''
| Filename    : map_flatfileids_in_query_file_to_igraph_format.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Jan 14 17:47:11 2016 (-0500)
| Last-Updated: Thu Jan 14 18:15:20 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 4
'''
import argparse, re
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
arg_parser.add_argument(
    '--flat2igraph_map_fn',
    default=('/export/projects/prastogi/kbvn/enron_'
             'contactgraph_flatfile_to_igraph_node_map'),
    type=str)
arg_parser.add_argument(
    '--query_fn', default='/home/hltcoe/ngao/miniScale-2016/Enron/queries',
    type=str)
arg_parser.add_argument(
    '--output_fn',
    default='/export/projects/prastogi/kbvn/enron_contactgraph_queries',
    type=str)
args=arg_parser.parse_args()
map_dict = dict(row.strip().split()
           for row
           in open(args.flat2igraph_map_fn, 'rb'))

ifh = open(args.query_fn, 'rb')
with open(args.output_fn, 'wb') as ofh:
    for row in ifh:
        row = row.strip().split('\t')
        qid = row[0]
        flatfile_node_ids = row[1][1:-1].split(', ')
        row_to_write = ' '.join([qid] + [map_dict[e] for e in flatfile_node_ids])
        ofh.write(row_to_write)
        ofh.write('\n')
