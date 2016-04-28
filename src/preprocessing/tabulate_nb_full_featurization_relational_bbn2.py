#!/usr/bin/env python
'''
| Filename    : tabulate_nb_full_featurization_relational_bbn2.py
| Description : Tabulate the Naive Bayes Runs.
| Author      : Pushpendre Rastogi
| Created     : Sun Apr 24 06:27:27 2016 (-0400)
| Last-Updated: Thu Apr 28 03:51:08 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 28
'''
from tabulate_eval_basic_featurization_relational_bbn2 import get_line, mci, headers
import re
from rasengan import confidence_interval_of_mean_with_unknown_variance as cim

dnd_header = ['s_features_backoff ',
              's_features_nodoc',
              's_features_doc',
              's_features_backoff_nodoc',
              'random', ]
import sys
import numpy as np

assert len(sys.argv) == 3
suffix = sys.argv[1]
metric_regex = [' CORRECTAUPR=([^ ]*) ', ' CORRECTP@10=([^ ]*)'][
    ['aupr', 'p10'].index(sys.argv[2])]

if __name__ == '__main__':
    data = list(
        open('../../scratch/nb_full_featurization_relational_bbn2.txt' + suffix))
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
