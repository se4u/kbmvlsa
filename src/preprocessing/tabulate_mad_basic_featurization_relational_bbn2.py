#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : tabulate_mad_basic_featurization_relational_bbn2.py
| Description : Tabulate the results of running modified adsorption on the knowledge graph.
| Author      : Pushpendre Rastogi
| Created     : Fri Apr 22 01:17:53 2016 (-0400)
| Last-Updated: Thu Apr 28 04:05:27 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 38
'''
from tabulate_eval_basic_featurization_relational_bbn2 import get_line, mci, headers
import re
import sys
from rasengan import confidence_interval_of_mean_with_unknown_variance as cim
import numpy as np

assert len(sys.argv) == 2
metric_regex = [' CORRECTAUPR=([^ ]*) ', ' CORRECTP@10=([^ ]*)'][
    ['aupr', 'p10'].index(sys.argv[1])]

if __name__ == '__main__':
    data = list(
        open('../../scratch/mad_basic_featurization_relational_bbn2.txt'))
    for dnd in ['wo_doc', 'with_doc', 'random', ]:
        l = []
        for hdr in headers:
            hdr_preamble = '%-60s' % ('~'.join(hdr))
            # print hdr_preamble,
            lines = get_line(data, dnd, *hdr)
            assert len(lines) == 5
            # reg_pat = ' AUPR=([^ ]*) CORRECTAUPR=([^ ]*) CORRECTP@10=([^ ]*)'
            # pat_out = [float(re.findall(' CORRECTAUPR=([^ ]*) ', line)[0])
            #            for line in lines]
            pat_out = [float(re.findall(metric_regex, line)[0])
                       for line in lines]
            mean, interval = cim(pat_out,
                                 alpha=0.9,
                                 sample_contains_all_of_population=False)
            if mean > 0:
                l.append([mean, (interval[1] - interval[0]) / 2])

        try:
            print ' & $', ' \pm '.join(['%2.1f' % (100 * e) for e in np.array(l).mean(axis=0)]), '$',
        except TypeError:
            import ipdb as pdb
            pdb.set_trace()
        #     print '&', mci(pat_out),
        # print
