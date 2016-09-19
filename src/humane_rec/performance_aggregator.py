#!/usr/bin/env python
'''
| Filename    : performance_aggregator.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Sep 19 01:58:06 2016 (-0400)
| Last-Updated: Mon Sep 19 02:01:16 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 5
'''
from collections import defaultdict
from rasengan.rank_metrics import average_precision
import random
import numpy


class PerformanceAggregator(object):

    def __init__(self, args=None):
        self.record = defaultdict(list)
        self.args = args

    def __call__(self, cat, scores, S_size, Q, verbose=True):
        fold = self.position(scores, set(Q))
        self.record[cat].append(fold)
        if verbose:
            print self.report_fold(cat, fold, S_size)

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

    @staticmethod
    def get_fold_stats(fold):
        arr = [0] * len(fold[1])
        for _, i in fold[2]:
            arr[i] = 1
        ap = average_precision(arr)
        # mean_reciprocal_rank(arr)
        mrr = 1.0 / (1 + min(e[1] for e in fold[2]))
        p_at_10 = float(sum(arr[:10])) / 10
        p_at_100 = float(sum(arr[:100])) / 100
        random.shuffle(arr)
        rap = average_precision(arr)
        # The Random MRR can be deterministically computed.
        rmrr = 1.0 / (1.0 + float(len(fold[1])) / (len(fold[2]) + 1))
        rp_at_10 = float(sum(arr[:10])) / 10
        rp_at_100 = float(sum(arr[:100])) / 100
        return [ap, rap, p_at_10, rp_at_10, p_at_100, rp_at_100, mrr, rmrr]

    def report_fold(self, cat, fold, S_size=-1):
        return ('%-40s(Training=%-3d,needles=%-3d,haystack=%-3d) '
                '(AUPR %.3f %.3f) (P@10 %.3f %.3f) (P@100 %.3f %.3f) '
                '(MRR %.3f %.3f)') % tuple(
                    [cat, S_size, len(fold[0]), len(fold[1])]
                    + self.get_fold_stats(fold))

    def __str__(self):
        fold_stats = [self.get_fold_stats(fold)
                      for cat in self.record
                      for fold in self.record[cat]]
        return ('(AUPR %.3f %.3f) (P@10 %.3f %.3f) (P@100 %.3f %.3f) '
                '(MRR %.3f %.3f)') % tuple(
                    numpy.array(fold_stats).mean(axis=0).tolist())
