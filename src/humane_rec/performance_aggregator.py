#!/usr/bin/env python
'''
| Filename    : performance_aggregator.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Sep 19 01:58:06 2016 (-0400)
| Last-Updated: Tue Sep 27 00:34:24 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 37
'''
from collections import defaultdict
from rasengan.rank_metrics import average_precision
import random
import numpy


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
        print self.stat_repr(
            ranking_stats(self.convert(scores, keep=train_idx, remove=test_idx)),
            shim=' ',
            domean=False)
        self.record[cat].append([scores, set(train_idx), set(test_idx), scratch])
        pass

    def __setitem__(self, key, value):
        self.record2[key]=value

    def convert(self, scores, keep, remove):
        ret = []
        for idx, s in enumerate(scores):
            if idx in remove:
                pass
            ret.append([s, int(idx in keep)])
        ret.sort(key=lambda x: x[0], reverse=True)
        return [e[1] for e in ret]

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
        for cat in self.record:
            for rec in self.record[cat]:
                scores, train_idx, test_idx = rec[0], rec[1], rec[2]
                train_fold_stats.append(
                    ranking_stats(self.convert(scores, keep=train_idx, remove=test_idx)))
                test_fold_stats.append(
                    ranking_stats(self.convert(scores, keep=test_idx, remove=train_idx)))
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
    print pkl.load(open('/export/b15/prastog3/catpeople_experiment.ppcfg~0.expcfg~0.pkl'))
