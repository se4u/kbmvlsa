#!/usr/bin/env python
'''
| Filename    : rank_according_to_modes.py
| Description : Rank entities according to modes.
| Author      : Pushpendre Rastogi
| Created     : Fri Aug 12 19:24:44 2016 (-0400)
| Last-Updated: Sun Aug 14 20:21:17 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 83
'''
import numpy as np
from rasengan import debug_support, tictoc, groupby
import cPickle as pkl
import math
import numpy as np
from collections import Counter


def get_mean_vec_from_modes(modes):
    return [np.mean([dcr2emb[m] for m in mode], axis=0)
            for mode in modes]


def get_mean_vec_from_cat(cat):
    return get_mean_vec_from_modes(cat2mode[cat])


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
    for dcr in groupby('data/random/results/summary.method.txt', yield_iter=True):
        pr = next(dcr).split('.')[0]
        cat = pr2cat[pr]
        modes = [e.replace(',', '').strip().split()[1:]
                 for e in dcr]
        ret[cat] = modes
    return ret


def tolerant_dot(mv, dcr, dcr2emb):
    if dcr in dcr2emb:
        return np.dot(mv, dcr2emb[dcr])

    dcr = dcr.lower()
    if dcr in dcr2emb:
        return np.dot(mv, dcr2emb[dcr])

    return float('-inf')


def harmonic_mean(x, y):
    return (float(x) * y) / (x + y) / 2

# --------------------------- #
# BEGIN SCRIPT FUNCTIONALITY  #
# --------------------------- #
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--cnt_transform', default='GM_SQRT_FREQ_SQRT_COUNT', type=str)
arg_parser.add_argument('--print_entity_list', default=1, type=int)
arg_parser.add_argument('--intervene_modes', default=1, type=int)
args = arg_parser.parse_args()

with tictoc('Loading emb pkl'):
    dcr2emb = pkl.load(open('data/demonstrate_similarity_idea.emb.pkl'))
    cat2mode = get_cat2mode()
    CONSTANT = (lambda x, t: 1)
    COUNT = (lambda x, t: x)
    LOG_COUNT = (lambda x, t: math.log(1 + x))
    SQRT_COUNT = (lambda x, t: math.sqrt(x))
    FREQ = (lambda x, t: float(x + 1) / (t + 1))
    SQ_FREQ = (lambda x, t: (float(x + 1) / (t + 1))**2)
    SQRT_FREQ = (lambda x, t: math.sqrt(float(x + 1) / (t + 1)))
    PROD_SQRT_FREQ_SQRT_COUNT = (
        lambda x, t: SQRT_COUNT(x, t) * SQRT_FREQ(x, t))
    GM_SQRT_FREQ_SQRT_COUNT = (
        lambda x, t: math.sqrt(SQRT_COUNT(x, t) * SQRT_FREQ(x, t)))
    cnt_transform = eval(args.cnt_transform)

with debug_support():
    def intervene_modes_hook(cat, modes):
        index_to_remove = []
        if cat == '20th-century_women_writers':
            index_to_remove = [1, 4]
        elif cat == 'American_television_reporters_and_correspondents':
            index_to_remove = [1, 4]
        elif cat == 'Recipients_of_the_Purple_Heart_medal':
            index_to_remove = [2, 3, 4]
        elif cat == 'United_States_Army_soldiers':
            index_to_remove = [2, 4]
        modes = [e for i, e in enumerate(modes) if i not in index_to_remove]
        return modes

    idi_list = []
    for cat in cat2mode:
        print '\nCATEGORY::', cat
        modes = cat2mode[cat]
        if args.intervene_modes:
            modes = intervene_modes_hook(cat, modes)
        # continue
        print '\n'.join([', '.join(e) for e in modes])
        mvs = get_mean_vec_from_modes(modes)
        cat_entity_score = {}
        for row in open('data/entity_descriptors_procoref~1.psv'):
            try:
                entity, dcrs = row.strip().split(' ||| ')
            except ValueError:
                continue
            else:
                pair_to_str_int = lambda x: [x[0], int(x[1])]
                dcrs = [pair_to_str_int(e.strip().split(':'))
                        for e in dcrs.strip().split()]
                total_cnt = sum(e[1] for e in dcrs)
                mode_feat = [
                    max(tolerant_dot(mv, dcr, dcr2emb) * cnt_transform(cnt, total_cnt)
                        for dcr, cnt in dcrs)
                    for mv in mvs]
                cat_entity_score[entity] = mode_feat
        known_entity_in_cat = set([e.strip() for e
                                   in open('data/category_to_entities/%s' % cat)])

        idi = []
        cat_entity_score = sorted(cat_entity_score.iteritems(),
                                  key=lambda x: sum(x[1]),
                                  reverse=True)
        for (idx, (e, s)) in enumerate(cat_entity_score):
            if args.print_entity_list:
                print e, s, e in known_entity_in_cat
            if e in known_entity_in_cat:
                idi.append([e, idx])
        print idi
        idi_list += idi
        pass
    rank_times = Counter([e[1] for e in idi_list]).items()
    print rank_times
    print 'MEAN RANK:', np.mean(map(lambda x: x[0] * x[1], rank_times))
