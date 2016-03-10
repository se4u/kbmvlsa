#!/usr/bin/env python
'''
| Filename    : create_adept_kb_pkl.py
| Description : Read
| Author      : Pushpendre Rastogi
| Created     : Wed Mar  9 20:10:29 2016 (-0500)
| Last-Updated: Thu Mar 10 00:47:50 2016 (-0500)
|           By: System User
|     Update #: 24
'''
import os
import cPickle as pickle

KBDIR='/export/projects/prastogi/adeptkb/'
entity_to_int_fn = KBDIR + 'entities_with_canonical_strings'

entity_to_int_map = dict((b.strip(),a)
                         for (a,b)
                         in enumerate(open(entity_to_int_fn)))
data_dict = {}
for row in open(os.path.expanduser('~/projects/kbvn/src/vncomparison/adept_kb_binary_relation.dat')):
    relation, e1, e2 = row.strip().split()
    fn1 = KBDIR + 'histog_dir/%s_events_%s'%(relation, e1)
    fn2 = KBDIR + 'histog_dir/%s_events_%s'%(relation, e2)
    aspect_name = '%s_%s_to_%s'%(relation, e1, e2)
    f1 = list(open(fn1))
    f2 = list(open(fn2))
    if len(f1) != len(f2):
        print 'WARNING: Uneven ', aspect_name + str((len(f1), len(f2))), 'CONTINUE!!'
        continue
    data_dict[aspect_name] = []
    for row1, row2 in zip(f1, f2):
        row1 = row1.strip().split()
        row2 = row2.strip().split()
        assert row1[0] == row2[0], 'Misaligned '+ aspect_name + ' BREAK!!'
        e1_ = row1[2][36:-1]
        e2_ = row2[2][36:-1]
        e1_idx = entity_to_int_map[e1_]
        e2_idx = entity_to_int_map[e2_]
        data_dict[aspect_name].append([e1_idx, e2_idx])
    print aspect_name, len(data_dict[aspect_name])

with open(KBDIR + 'adept.pkl', 'wb') as f:
    pickle.dump(
        dict(entity_to_int_map=entity_to_int_map, data_dict=data_dict),
        f)
#  Local Variables:
#  eval: (progn (anaconda-mode -1) (company-mode -1) (eldoc-mode -1))
#  eval: (progn (flycheck-mode -1) (hs-minor-mode -1))
#  End:
