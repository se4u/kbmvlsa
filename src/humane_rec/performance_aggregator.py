#!/usr/bin/env python
'''
| Filename    : performance_aggregator.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Sep 19 01:58:06 2016 (-0400)
| Last-Updated: Tue Sep 27 07:51:43 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 60
'''
from collections import defaultdict
from rasengan.rank_metrics import average_precision
import random
import numpy
from rasengan import tictoc

def ranking_stats(arr):
    ap = average_precision(arr)
    mrr = 1.0 / (1 + arr.index(1))
    p_at_10 = float(sum(arr[:10])) / 10
    p_at_100 = float(sum(arr[:100])) / 100

    random.shuffle(arr)
    rap = average_precision(arr)
    rmrr = 1.0 / (1 + arr.index(1))
    rp_at_10 = float(sum(arr[:10])) / 10
    rp_at_100 = float(sum(arr[:100])) / 100
    return [ap, rap, p_at_10, rp_at_10, p_at_100, rp_at_100, mrr, rmrr]


class Aggregator(object):
    def __init__(self, datacfg, ppcfg, expcfg, url_list, TM):
        self.record = defaultdict(list)
        self.record2 = {}
        self.datacfg = datacfg
        self.ppcfg = ppcfg
        self.expcfg =  expcfg
        self.url_list = url_list
        self.TM = TM

    def __call__(self, cat, scores, train_idx, test_idx, scratch=None):
        scores = self.process(scores, train_idx, test_idx)
        self.record[cat].append([scores, scratch])
        print self.stat_repr(ranking_stats(self.convert(scores)), shim=' ', domean=False)
        return

    def process(self, scores, train_idx, test_idx):
        train_idx, test_idx = set(train_idx), set(test_idx)
        l = []
        for idx, s in enumerate(scores):
            if not isinstance(s, float):
                s = s[0,0]
            if idx in train_idx:
                l.append([s, 2])
            elif idx in test_idx:
                l.append([s,1])
            else:
                l.append([s,0])
        l.sort(key=lambda x: x[0], reverse=True)
        return l

    def __setitem__(self, key, value):
        self.record2[key]=value

    def convert(self, scores, limit=0):
        # return [flag for s, flag in scores if flag != 2]
        tmp = [flag for s, flag in scores if flag != 2]
        idi = [i for i,e in enumerate(tmp) if e == 0]
        random.shuffle(idi)
        idi = set(idi[:1000])
        return [e for i,e in enumerate(tmp) if i in idi or e == 1]

    @staticmethod
    def stat_repr(stats, shim='\n', domean=True):
        STATS = 'AUPR RAUPR P@10 RP@10 P@100 RP@100 MRR RMRR'
        if domean:
            mean = numpy.array(stats).mean(axis=0).tolist()
        else:
            mean = stats
        return shim.join('%-6s %.4f'%(a,b)
                         for (a,b)
                         in zip(STATS.split(), mean))

    def __str__(self):
        train_fold_stats = []
        test_fold_stats = []
        limit = (self.limit if hasattr(self, 'limit') else 0)
        for cat in self.record:
            for rec in self.record[cat]:
                scores = rec[0]
                train_fold_stats.append(ranking_stats(self.convert(scores, limit=limit)))
                test_fold_stats.append(ranking_stats(self.convert(scores, limit=limit)))
        return '\n'.join(['--Train--',
                          self.stat_repr(train_fold_stats),
                          '--Test--',
                          self.stat_repr(test_fold_stats)])



class Performance_Aggregator(object):

    def __init__(self, args=None):
        self.record = defaultdict(list)
        self.args = args

    @staticmethod
    def position(scores, Q):
        return (Q,
                scores,
                [(entity, rank)
                 for rank, (entity, _score)
                 in enumerate(sorted(scores.iteritems(),
                                     key=lambda x: x[1],
                                     reverse=True))
                 if entity in Q])

    def __call__(self, cat, scores, S_size, Q, verbose=True):
        fold = self.position(scores, set(Q))
        self.record[cat].append(fold)
        if verbose:
            print self.report_fold(cat, fold, S_size)

    @staticmethod
    def get_fold_stats(fold):
        arr = [0] * len(fold[1])
        for _, i in fold[2]:
            arr[i] = 1
        return ranking_stats(arr)

    def report_fold(self, cat, fold, S_size=-1):
        return ('%-40s(Training=%-3d,needles=%-3d,haystack=%-3d) '
                '(AUPR %.3f %.3f) (P@10 %.3f %.3f) (P@100 %.3f %.3f) '
                '(MRR %.3f %.3f)') % tuple(
                    [cat, S_size, len(fold[0]), len(fold[1])]
                    + self.get_fold_stats(fold))

    def fold_stats(self, add_cat=False):
        if add_cat:
            return [[cat, fold_idx] + self.get_fold_stats(fold)
                    for cat in self.record
                    for fold_idx, fold in enumerate(self.record[cat])]
        else:
            return [self.get_fold_stats(fold)
                    for cat in self.record
                    for fold in self.record[cat]]

    def __str__(self):
        fold_stats = self.fold_stats()
        return ('(AUPR %.3f %.3f) (P@10 %.3f %.3f) (P@100 %.3f %.3f) '
                '(MRR %.3f %.3f)') % tuple(
                    numpy.array(fold_stats).mean(axis=0).tolist())


if __name__ == '__main__':
    import cPickle as pkl
    for f in [
            '/export/b15/prastog3/catpeople_experiment.ppcfg~8.expcfg~303.pkl'
            # '/export/b15/prastog3/catpeople_experiment.ppcfg~0.expcfg~0.pkl',
            # '/export/b15/prastog3/catpeople_experiment.ppcfg~7.expcfg~0.pkl',
    ]:
        print '--------- FILE: ', f
        with tictoc('Loading Pkl'):
            data = pkl.load(open(f))
        # data.limit=1000
        print data
# --------- FILE:  /export/b15/prastog3/catpeople_experiment.ppcfg~0.expcfg~0.pkl
# --Train--
# AUPR   0.0798
# RAUPR  0.0004
# P@10   0.1100
# RP@10  0.0000
# P@100  0.0311
# RP@100 0.0002
# MRR    0.3081
# RMRR   0.0013
# --Test--
# AUPR   0.0161
# RAUPR  0.0002
# P@10   0.0140
# RP@10  0.0000
# P@100  0.0077
# RP@100 0.0003
# MRR    0.0462
# RMRR   0.0006
# --------- FILE:  /export/b15/prastog3/catpeople_experiment.ppcfg~7.expcfg~0.pkl
# --Train--
# AUPR   0.0403
# RAUPR  0.0004
# P@10   0.0670
# RP@10  0.0000
# P@100  0.0190
# RP@100 0.0001
# MRR    0.2466
# RMRR   0.0014
# --Test--
# AUPR   0.0117
# RAUPR  0.0003
# P@10   0.0080
# RP@10  0.0000
# P@100  0.0046
# RP@100 0.0002
# MRR    0.0419
# RMRR   0.0011
# --------- FILE:  /export/b15/prastog3/catpeople_experiment.ppcfg~8.expcfg~303.pkl
#   --Train--
#   AUPR   0.0162
#   RAUPR  0.0002
#   P@10   0.0160
#   RP@10  0.0000
#   P@100  0.0066
#   RP@100 0.0000
#   MRR    0.0606
#   RMRR   0.0004
#   --Test--
#   AUPR   0.0162
#   RAUPR  0.0003
#   P@10   0.0160
#   RP@10  0.0000
#   P@100  0.0066
#   RP@100 0.0001
#   MRR    0.0606
#   RMRR   0.0011


# AUPR   0.1623
# RAUPR  0.0153
# P@10   0.1270
# RP@10  0.0070
# P@100  0.0412
# RP@100 0.0086
# MRR    0.3337
# RMRR   0.0375
