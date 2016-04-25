#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : tabulate_mad_basic_featurization_relational_bbn2.py
| Description : Tabulate the results of running modified adsorption on the knowledge graph.
| Author      : Pushpendre Rastogi
| Created     : Fri Apr 22 01:17:53 2016 (-0400)
| Last-Updated: Fri Apr 22 10:53:13 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 35
'''
from tabulate_eval_basic_featurization_relational_bbn2 import get_line, mci, headers
import re

if __name__ == '__main__':
    data = list(
        open('../../scratch/mad_basic_featurization_relational_bbn2.txt'))
    for hdr in headers:
        hdr_preamble = '%-60s' % ('~'.join(hdr))
        print hdr_preamble,
        for dnd in ['wo_doc', 'with_doc', 'random', ]:
            lines = get_line(data, dnd, *hdr)
            assert len(lines) == 5
            # reg_pat = ' AUPR=([^ ]*) CORRECTAUPR=([^ ]*) CORRECTP@10=([^ ]*)'
            pat_out = [float(re.findall(' CORRECTAUPR=([^ ]*) ', line)[0])
                       for line in lines]
            print '&', mci(pat_out),
        print
