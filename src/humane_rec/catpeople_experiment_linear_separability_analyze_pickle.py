#!/usr/bin/env python
'''
| Filename    : catpeople_experiment_linear_separability_analyze_pickle.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Fri Sep 30 23:11:33 2016 (-0400)
| Last-Updated: Fri Sep 30 23:16:48 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 3
'''
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
arg_parser.add_argument('--pkl_fn', default='/export/b15/prastog3/catpeople_ls.ppcfg~0.expcfg~16.pkl', type=str)
args=arg_parser.parse_args()

import cPickle as pkl
data = pkl.load(open(args.pkl_fn, 'rb'))
import pdb
pdb.set_trace()
