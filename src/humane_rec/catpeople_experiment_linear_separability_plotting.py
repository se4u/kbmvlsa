#!/usr/bin/env python
'''
| Filename    : catpeople_experiment_linear_separability_plotting.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Fri Sep 30 10:56:54 2016 (-0400)
| Last-Updated: Sat Oct  1 21:06:30 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 170
'''
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--ppcfg', default=None, type=int, help='Default={None}')
arg_parser.add_argument('--figsize_x', default=10, type=int)
arg_parser.add_argument('--figsize_y', default=5, type=int)
arg_parser.add_argument('--title', default=None, type=str)
arg_parser.add_argument('--out_fn', default=None, type=str)
arg_parser.add_argument('--xmin', default=0, type=float)
arg_parser.add_argument('--ymin', default=0.5, type=float)
arg_parser.add_argument('--expcfg_str', default='16 9 26', type=str)
args=arg_parser.parse_args()
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from util_catpeople_experiment_linear_separability_plotting import \
    get_stats, lcmap, getline2d
from rasengan import debug_support
with debug_support():
    aupr, mrr, color, C, shape = get_stats(args.ppcfg, expcfg_str=args.expcfg_str)
    fig = plt.figure(figsize=(args.figsize_x, args.figsize_y)) # give plots a rectangular frame
    ax = fig.add_subplot(111)
    label_to_artists = {}
    for i, (a,m,c, c_,s) in enumerate(zip(aupr, mrr, color, C,shape)):
        print a, m, c, c_, s
        if s == 'circle':
            label = 'Test %s'%lcmap[c]
            label_to_artists[label] = ax.add_artist(
                plt.Circle((a,m), .005, color=c, alpha=0.3, label=label))
        else:
            label = 'Train %s'%lcmap[c]
            label_to_artists[label] = ax.add_artist(
                plt.Rectangle((a-.005,m-.005), 0.01, 0.01,
                              color=c, alpha=0.3,
                              label=label))
        tb = plt.text(a+.01, .99*m, 'C=%.1f'%c_,
                      fontsize=10,
                      verticalalignment='top',
                      alpha=0.7)
    plt.xlim(xmin=min(aupr) - 0.05 if args.xmin is None else args.xmin)
    plt.ylim(ymin=min(mrr) - 0.05  if args.ymin is None else args.ymin)
    plt.xlabel('AUPR')
    plt.ylabel('MRR')
    plt.title(args.title)
    plt.grid(True)
    label, handle = zip(*label_to_artists.items())
    plt.legend([getline2d(e) for e in handle],
               label,
               loc='lower right',
               numpoints=1)
    plt.savefig(args.out_fn)
    plt.close()
