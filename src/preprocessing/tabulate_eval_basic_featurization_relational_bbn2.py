#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : tabulate_eval_basic_featurization_relational_bbn2.py
| Description : Tabulate the output of the eval_basic_script
| Author      : Pushpendre Rastogi
| Created     : Thu Apr 21 12:34:14 2016 (-0400)
| Last-Updated: Wed Apr 27 23:28:13 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 36
'''
import rasengan

headers = [[_.strip() for _ in e.strip().split(' & ')] for e in '''
adept-core#Role                 & role         & "author"
adept-core#Role                 & role         & "director"
adept-core#EmploymentMembership & employer     & "Army"
adept-core#EmploymentMembership & employer     & "White_House"
adept-core#Resident             & location     & "Chinese"
adept-core#Resident             & location     & "Texas"
adept-core#Leadership           & subject_org  & "Democratic"
adept-core#Leadership           & subject_org  & "Parliament"
adept-core#Origin               & origin       & "American"
adept-core#Origin               & origin       & "Russia"
adept-core#StudentAlum          & almamater    & "Harvard"
adept-core#StudentAlum          & almamater    & "Stanford"
'''.strip().split('\n')]


def get_line(data, *args):
    return [e.replace("White House", "White_House").strip()
            for e
            in data
            if all(_ in e.replace("White House", "White_House") for _ in args)]


def mci(obs):
    mean, interval = rasengan.confidence_interval_of_mean_with_unknown_variance(
        obs, alpha=0.9, sample_contains_all_of_population=False)
    return '$%.3f \pm %.3f $' % (mean, (interval[1] - interval[0]) / 2)

if __name__ == '__main__':
    data = list(open('../../scratch/eval_basic_featurization_bbn2_v2.txt'))
    mask_pattern = {'method+doc': 'mask_pattern.pattern=XXXX',
                    'method': 'mask_pattern.pattern=~document~.*'}
    prefix = 'Criteria='
    train_row = 'train_rows=10'
    coef_type = ['coef_type=clipped', 'coef_type=original'][1]
    for hdr in headers:
        def process_lines(mp):
            lines = get_line(data, prefix, train_row, mp, coef_type, *hdr)
            try:
                lines = [dict([_.split('=') for _ in e.strip().split()])
                         for e in lines]
            except ValueError:
                import ipdb as pdb
                pdb.set_trace()
            if len(lines) == 0:
                import ipdb as pdb
                pdb.set_trace()
            return lines

        lm = process_lines(mask_pattern['method'])
        lmd = process_lines(mask_pattern['method+doc'])
        p_at_10 = [float(e['P@10']) for e in lm]
        p_at_10_doc = [float(e['P@10']) for e in lmd]
        random_p_at_10 = [float(e['BASE-P@10']) for e in lm + lmd]
        aupr = [float(e['AUPR']) for e in lm]
        aupr_doc = [float(e['AUPR']) for e in lmd]
        random_aupr = [float(e['BASE-AUPR']) for e in lm + lmd]
        try:
            print '%-60s' % ('~'.join(hdr)), mci(p_at_10), '&' , mci(p_at_10_doc), '&' , mci(random_p_at_10), '&' ,\
                mci(aupr), '&', mci(aupr_doc), '&', mci(random_aupr)
        except ValueError:
            import ipdb as pdb
            pdb.set_trace()
