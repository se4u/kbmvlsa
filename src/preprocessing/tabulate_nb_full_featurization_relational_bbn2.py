#!/usr/bin/env python
'''
| Filename    : tabulate_nb_full_featurization_relational_bbn2.py
| Description : Tabulate the Naive Bayes Runs.
| Author      : Pushpendre Rastogi
| Created     : Sun Apr 24 06:27:27 2016 (-0400)
| Last-Updated: Sun Apr 24 06:34:01 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 5
'''
from tabulate_eval_basic_featurization_relational_bbn2 import get_line, mci, headers
import re

if __name__ == '__main__':
    data = list(
        open('../../scratch/nb_full_featurization_relational_bbn2.txt'))
    for hdr in headers:
        hdr_preamble = '%-60s' % ('~'.join(hdr))
        print hdr_preamble,
        for dnd in ['s_features_backoff ', 's_features_nodoc', 's_features_backoff_nodoc', 'random', ]:
            lines = get_line(data, dnd, *hdr)
            assert len(lines) == 5
            # reg_pat = ' AUPR=([^ ]*) CORRECTAUPR=([^ ]*) CORRECTP@10=([^ ]*)'
            pat_out = [float(re.findall(' CORRECTAUPR=([^ ]*) ', line)[0])
                       for line in lines]
            print '&', mci(pat_out),
        print
