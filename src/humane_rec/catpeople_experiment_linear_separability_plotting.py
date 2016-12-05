#!/usr/bin/env python
'''
| Filename    : catpeople_experiment_linear_separability_plotting.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Fri Sep 30 10:56:54 2016 (-0400)
| Last-Updated: Sun Oct  2 15:05:50 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 205
'''
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from util_catpeople_experiment_linear_separability_plotting import \
    get_stats, getline2d
from rasengan import debug_support
from numpy.random import rand
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--ppcfg', default=None, type=int, help='Default={None}')
arg_parser.add_argument('--figsize_x', default=10, type=int)
arg_parser.add_argument('--figsize_y', default=10, type=int)
arg_parser.add_argument('--title', default=None, type=str)
arg_parser.add_argument('--out_fn', default=None, type=str)
arg_parser.add_argument('--xmin', default=0, type=float)
arg_parser.add_argument('--ymin', default=0, type=float)
arg_parser.add_argument('--expcfg_str', default='10 14 15 16 9 26', type=str)
arg_parser.add_argument('--pptitle', default=None, nargs='+', type=str)
arg_parser.add_argument('--cmap', default='Paired', type=str)
args=arg_parser.parse_args()

def get_ppcfg_title(pptitle):
    tmp = pptitle.find(' ')
    ppcfg = int(pptitle[:tmp])
    title = pptitle[tmp+1:]
    return ppcfg, title

def translate(title):
    return title.translate(None,' (),.')

def main():
    if args.out_fn is None:
        basename = ''.join([translate(get_ppcfg_title(e)[1])
                            for e
                            in args.pptitle])
        args.out_fn = 'figures/%s.pdf'%(basename)

    with debug_support():
        fig = plt.figure(figsize=(args.figsize_x, args.figsize_y)) # give plots a rectangular frame
        ax = fig.add_subplot(111)
        label_to_artists = {}
        cm = plt.get_cmap(args.cmap)
        for pptitle_idx, pptitle in enumerate(args.pptitle):
            ppcfg, title = get_ppcfg_title(pptitle)
            aupr, mrr, _, C, shape = get_stats(ppcfg, expcfg_str=args.expcfg_str)
            for (a, m, c_, s) in zip(aupr, mrr, C, shape):
                c = cm(.1*pptitle_idx)
                print a, m, c, c_, s
                if s == 'circle':
                    label = 'Test %s'%title
                    label_to_artists[label] = ax.add_artist(
                        plt.Circle((a,m), .005, color=c,
                                   alpha=0.7, label=label))
                else:
                    label = 'Train %s'%title
                    label_to_artists[label] = ax.add_artist(
                        plt.Rectangle((a-.005,m-.005),
                                      0.01,
                                      0.01,
                                      color=c, alpha=0.7,
                                      label=label))
                plt.text(a+.01,
                         m + .000 * round(rand()),
                         '%s %.1f'%(title.replace('Hinge ', ''),
                                    c_),
                         fontsize=2,
                         # verticalalignment='top',
                         alpha=0.7)
            plt.xlim(xmin=min(aupr) - 0.05
                     if args.xmin is None
                     else args.xmin)
            plt.ylim(ymin=min(mrr) - 0.05
                     if args.ymin is None
                     else args.ymin)
            plt.xlabel('AUPR')
            plt.ylabel('MRR')
            plt.title('Various Feature Sets at Different C')
            plt.grid(True)
            continue
        label, handle = zip(*sorted(label_to_artists.items(), key=lambda x: x[0]))
        plt.legend([getline2d(e) for e in handle],
                   label,
                   loc='lower right',
                   numpoints=1)
        pass
    print 'Saving file', args.out_fn
    plt.savefig(args.out_fn)
    plt.close()
    return


if __name__ == '__main__':
    main()
