#!/usr/bin/env python
'''
| Filename    : rank_according_to_modes.py
| Description : Rank entities according to modes.
| Author      : Pushpendre Rastogi
| Created     : Fri Aug 12 19:24:44 2016 (-0400)
| Last-Updated: Fri Aug 12 22:12:25 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 33
'''
import numpy as np
from rasengan import debug_support, tictoc, groupby
import cPickle as pkl


def get_cat2mode():
    pr2cat = {'eddd3': '1945_births',
              '4b43': 'American_television_reporters_and_correspondents',
              '0967': 'Recipients_of_the_Purple_Heart_medal',
              '5d65': '20th-century_women_writers',
              '7a65': 'American_political_writers',
              'a295': 'Recipients_of_the_Bronze_Star_Medal',
              'e854': 'English_masculine_given_names',
              '27b2': 'United_States_Army_soldiers',
              'ec22': '2004_deaths',
              '42ca': 'American_Presbyterians'}
    ret = {}
    ret2 = {}
    for dcr in groupby('data/random/results/summary.method.txt', yield_iter=True):
        pr = next(dcr).split('.')[0]
        cat = pr2cat[pr]
        modes = [e.replace(',', '').strip().split()[1:]
                 for e in dcr]
        ret[cat] = modes
        ret2[cat] = [np.mean([dcr2emb[m] for m in mode], axis=0)
                     for mode in modes]
    return ret, ret2


def tolerant_dot(mv, dcr, dcr2emb):
    if dcr in dcr2emb:
        return np.dot(mv, dcr2emb[dcr])

    dcr = dcr.lower()
    if dcr in dcr2emb:
        return np.dot(mv, dcr2emb[dcr])

    return float('-inf')

with tictoc('Loading emb pkl'):
    dcr2emb = pkl.load(open('data/demonstrate_similarity_idea.emb.pkl'))
    cat2mode, cat2mv = get_cat2mode()

with debug_support():
    for cat, mvs in cat2mv.iteritems():
        cat_entity_score = {}
        for row in open('data/entity_descriptors_procoref~1.psv'):
            try:
                entity, dcrs = row.strip().split(' ||| ')
            except ValueError:
                continue
            else:
                dcrs = [e.strip().split(':')[0]
                        for e in dcrs.strip().split()]
                mode_feat = [max([tolerant_dot(mv, dcr, dcr2emb)
                                  for dcr in dcrs])
                             for mv in mvs]
                cat_entity_score[entity] = mode_feat
        known_entity_in_cat = set([e.strip() for e
                                   in open('data/category_to_entities/%s' % cat)])
        print '\n', cat
        print '\n'.join([', '.join(e) for e in cat2mode[cat]])
        idi = []
        cat_entity_score = sorted(cat_entity_score.iteritems(),
                                  key=lambda x: sum(x[1]),
                                  reverse=True)
        for (idx, (e, s)) in enumerate(cat_entity_score):
            # print e, s, e in known_entity_in_cat
            if e in known_entity_in_cat:
                idi.append([e, idx])
        print idi
