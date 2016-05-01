#!/usr/bin/env python
'''
| Filename    : tabulate_nb_full_featurization_relational_bbn2.py
| Description : Tabulate the Naive Bayes Runs.
| Author      : Pushpendre Rastogi
| Created     : Sun Apr 24 06:27:27 2016 (-0400)
| Last-Updated: Sat Apr 30 21:55:37 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 32
'''
from tabulate_eval_basic_featurization_relational_bbn2 import get_line, headers, everything
import re
import sys

assert len(sys.argv) == 2
suffix = ''
metric_regex = [' CORRECTAUPR=([^ ]*) ', ' CORRECTP@10=([^ ]*)'][
    ['aupr', 'p10'].index(sys.argv[1])]

if __name__ == '__main__':
    data = list(
        open('../../scratch/nb_full_featurization_relational_bbn2.txt' + suffix))
    for dnd in ['s_features_backoff ',
                's_features_nodoc',
                's_features_doc',
                's_features_backoff_nodoc',
                'random', ]:
        pat_out_l = []
        for hdr in headers:
            hdr_preamble = '%-60s' % ('~'.join(hdr))
            lines = get_line(data, dnd, *hdr)
            assert len(lines) == 5
            pat_out_l.append([e
                              for e
                              in [float(re.findall(metric_regex, line)[0])
                                  for line in lines]
                              if e != -1])
        everything(pat_out_l)
