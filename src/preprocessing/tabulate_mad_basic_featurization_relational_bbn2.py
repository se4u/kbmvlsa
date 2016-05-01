#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : tabulate_mad_basic_featurization_relational_bbn2.py
| Description : Tabulate the results of running modified adsorption on the knowledge graph.
| Author      : Pushpendre Rastogi
| Created     : Fri Apr 22 01:17:53 2016 (-0400)
| Last-Updated: Sat Apr 30 21:53:34 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 58
'''
from tabulate_eval_basic_featurization_relational_bbn2 import get_line, headers, everything
import re
import sys

assert len(sys.argv) == 2
metric_regex = [' CORRECTAUPR=([^ ]*) ', ' CORRECTP@10=([^ ]*)'][
    ['aupr', 'p10'].index(sys.argv[1])]


if __name__ == '__main__':
    data = list(
        open('../../scratch/mad_basic_featurization_relational_bbn2.txt'))
    for dnd in ['wo_doc', 'with_doc', 'random', ]:
        pat_out_l = []
        for hdr in headers:
            hdr_preamble = '%-60s' % ('~'.join(hdr))
            lines = get_line(data, dnd, *hdr)
            assert len(lines) == 5
            pat_out_l.append(
                [e
                 for e
                 in [float(re.findall(metric_regex, line)[0])
                     for line in lines]
                 if e != -1])
        # print pat_out_l
        everything(pat_out_l)
