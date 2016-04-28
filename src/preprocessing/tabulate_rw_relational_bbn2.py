#!/usr/bin/env python
'''
| Filename    : tabulate_rw_relational_bbn2.py
| Description : Tabulate the rw results.
| Author      : Pushpendre Rastogi
| Created     : Thu Apr 28 09:00:16 2016 (-0400)
| Last-Updated: Thu Apr 28 09:05:40 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
from tabulate_eval_basic_featurization_relational_bbn2 import get_line, mci, headers
import re
from rasengan import confidence_interval_of_mean_with_unknown_variance as cim

dnd_header = [
    's_features_nodoc',
    's_features_doc',
]
import sys
import numpy as np

import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
arg_parser.add_argument('metric', default='aupr', type=str)
args = arg_parser.parse_args()
metric_regex = [' CORRECTAUPR=([^ ]*) ', ' CORRECTP@10=([^ ]*)'][
    ['aupr', 'p10'].index(args.metric)]

if __name__ == '__main__':
    data = list(
        open('../../scratch/rw_relational_bbn2.txt'))
    # print '\t'.join(dnd_header)
    for dnd in dnd_header:
        l = []
        for hdr in headers:
            hdr_preamble = '%-60s' % ('~'.join(hdr))
            lines = get_line(data, dnd, *hdr)
            if len(lines) != 5:
                import ipdb as pdb
                pdb.set_trace()
            # reg_pat = ' AUPR=([^ ]*) CORRECTAUPR=([^ ]*) CORRECTP@10=([^ ]*)'
            pat_out = [float(re.findall(metric_regex, line)[0])
                       for line in lines]
            mean, interval = cim(pat_out,
                                 alpha=0.9,
                                 sample_contains_all_of_population=False)
            if mean > 0:
                l.append([mean, (interval[1] - interval[0]) / 2])

        print ' & $', ' \pm '.join(['%2.1f' % (100 * e) for e in np.array(l).mean(axis=0)]), '$',
