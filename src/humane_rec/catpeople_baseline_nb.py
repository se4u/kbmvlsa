#!/usr/bin/env python
'''
| Filename    : catpeople_baseline_nb.py
| Description : The Baseline NB experiment.
| Author      : Pushpendre Rastogi
| Created     : Sun Sep  4 18:32:35 2016 (-0400)
| Last-Updated: Thu Sep  8 02:25:05 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 162
This script implements the NB baseline described in Section 3.1 of the humane_rec paper.
'''
import random
import numpy as np
random.seed(0)
np.random.seed(0)
from math import log
import argparse
import sys
from shelve import DbfilenameShelf
import cPickle as pkl
import rasengan
from rasengan import TokenMapper
from collections import Counter, defaultdict
import itertools
from rasengan.rank_metrics import average_precision
import catpeople_baseline_nb_config


def get(l, idi):
    return [l[i] for i in idi]


def minus(E, S):
    S = set(S)
    return [e for e in E if e not in S]


class TextualClueObject(object):

    def __init__(self, S, url_mentions, token_map_obj,
                 max_tok=catpeople_baseline_nb_config.MAX_TOK,
                 entire=True,
                 binarized_mnb=True):
        self.S = S
        self.Se_list = [url_mentions[e] for e in S]
        self.entire = entire
        # self.lower = lower
        self.binarized_mnb = binarized_mnb
        self.max_tok = max_tok
        self.BOS = max_tok - 1
        # Sets self.features, self.fS
        self.order_unigrams_and_bigrams()
        self.tmo = token_map_obj

    def order_unigrams_and_bigrams(self):
        self.fS = {}
        self.features = {}
        for e, Se in itertools.izip(self.S, self.Se_list):
            e_feat = self.create_ngrams(Se, 1)
            e_feat.update(self.create_ngrams(Se, 2))
            self.features[e] = e_feat
        self.fS = set(rasengan.flatten((
            list(v) for v in self.features.itervalues())))
        return

    def create_ngrams(self, Se, n, predicate=None, verbose=False):
        # NOTE: We are implementing the Binarized MNB model where we dont
        # multiple count features that occur in a single
        # document/utterange/sentence.
        assert self.binarized_mnb
        features = {}
        max_tok = self.max_tok
        total_iter = 0
        if predicate is None:
            predicate = lambda x: True
        for mention in Se:
            tokens = (rasengan.flatten(mention[0])
                      if self.entire
                      else mention[0][mention[1]])
            if n == 1:
                for t in tokens:
                    total_iter += 1
                    if predicate(t):
                        features[t] = None
            elif n == 2:
                # This is the BOS token idx
                pt = self.BOS
                for ct in tokens:
                    total_iter += 1
                    bigram_feature = max_tok * (1 + pt) + ct
                    pt = ct
                    if predicate(bigram_feature):
                        features[bigram_feature] = None
            elif n == 12:
                pt = self.BOS
                for ct in tokens:
                    total_iter += 1
                    bigram_feature = max_tok * (1 + pt) + ct
                    pt = ct
                    if predicate(bigram_feature):
                        features[bigram_feature] = None
                    if predicate(ct):
                        features[ct] = None
            else:
                raise NotImplementedError
        if verbose:
            print 'Total_iter', total_iter
        return features


class NBRecommender(object):

    def __init__(self, clue_obj,
                 threshold=False,
                 alpha=1,
                 adaptive_alpha=False,
                 ngram_occurrence=5.0 / 10.0,):
        self.clue_obj = clue_obj
        self.w = {}
        if adaptive_alpha:
            self.alpha = len(clue_obj.S) * ngram_occurrence
        else:
            self.alpha = alpha
        for feat in clue_obj.fS:
            wprime = (sum(1 for e in clue_obj.S if feat in clue_obj.features[e])
                      / self.alpha)
            if threshold:
                self.w[feat] = log(1 + int(wprime))
            else:
                self.w[feat] = log(1 + wprime)

    def __call__(self, Se):
        w = self.w
        cn = self.clue_obj.create_ngrams
        return sum(w[feat]
                   for n in [1, 2]
                   for feat in cn(Se, n)
                   if feat in w)


class FunctionWordRemover(object):

    def __init__(self, rec_obj, remove_bigram=True, limit_features=20):
        from rasengan.function_words import get_function_words
        self.rec_obj = rec_obj
        self.w = dict(rec_obj.w)
        tmo = rec_obj.clue_obj.tmo
        bad_idx = []
        for e in get_function_words():
            e = e.lower()
            try:
                idx = tmo([e])[0]
                del self.w[idx]
                bad_idx.append(idx)
            except KeyError:
                continue
        if remove_bigram:
            for index in self.w.keys():
                ct = index % catpeople_baseline_nb_config.MAX_TOK
                pt = ((index - ct) / catpeople_baseline_nb_config.MAX_TOK - 1)
                if pt in bad_idx or ct in bad_idx:
                    del self.w[index]
        if limit_features:
            good_feat = set(
                sorted(self.w.iterkeys(), key=lambda x: self.w[x], reverse=True)[:limit_features])
            for feat in self.w.keys():
                if feat not in good_feat:
                    del self.w[feat]

    def __call__(self, Se):
        cn = self.rec_obj.clue_obj.create_ngrams
        w = self.w
        predicate = lambda x: x in w
        val = sum(w[feat] for feat in cn(Se, 12, predicate=predicate))
        return val

    def report(self, limit=20):
        print 'Total Features', len(self.w)
        for idx, (a, b) in enumerate(
                sorted(self.w.iteritems(), key=lambda x: x[1], reverse=True)):
            if idx < limit:
                print (self.rec_obj.clue_obj.tmo[a], b)


class Performance_Aggregator(object):

    def __init__(self):
        self.record = defaultdict(list)

    def __call__(self, cat, scores, S_size, Q, verbose=True):
        fold = self.position(scores, set(Q))
        self.record[cat].append(fold)
        if verbose:
            print self.report_fold(cat, fold, S_size)

    def position(self, scores, Q):
        return (Q,
                scores,
                [(entity, rank)
                 for rank, (entity, score)
                 in enumerate(sorted(scores.iteritems(),
                                     key=lambda x: x[1],
                                     reverse=True))
                 if entity in Q])

    def report_fold(self, cat, fold, S_size=-1):
        arr = [0] * len(fold[1])
        for _, i in fold[2]:
            arr[i] = 1
        ap = average_precision(arr)
        random.shuffle(arr)
        rap = average_precision(arr)
        return '%-40s(Training=%-3d,needles=%-3d,haystack=%-3d) %.3f %.3f' % (
            cat, S_size, len(fold[0]), len(arr), ap, rap)

    def __str__(self):
        return '\n'.join(self.report_fold(cat, fold)
                         for cat in self.record
                         for fold in self.record[cat])


def main():
    url_mention = DbfilenameShelf(args.in_shelf, protocol=-1, flag='r')
    E = url_mention['__URL_LIST__']
    TM = url_mention['__TOKEN_MAPPER__']
    TM.finalize(catpeople_baseline_nb_config.MAX_TOK)
    cat_folds = pkl.load(open(args.fold_fn))
    cat2url = dict((caturl_group[0].split()[0], [e.strip().split()[1] for e in caturl_group])
                   for caturl_group
                   in rasengan.groupby(args.cat2url_fn, predicate=lambda x: x.split()[0]))
    performance_aggregator = Performance_Aggregator()
    rasengan.warn('Using Reduced number of categories and folds')
    for cat_idx, (cat, folds) in enumerate(cat_folds.items()[:10]):
        print >> sys.stderr, 'cat_idx = %.2f\r' % (cat_idx),
        for (train_idx, test_idx) in folds:
            for train_set_size in [0.5, 1]:
                S = get(
                    cat2url[cat], train_idx[:int(len(train_idx) * train_set_size)])
                EmS = minus(E, S)
                Q = get(cat2url[cat], test_idx)
                EmSQ = minus(EmS, Q)
                # --------------------- #
                # Extract Textual Clues #
                # --------------------- #
                clue_obj = TextualClueObject(S, url_mention, TM)
                # ------------------------------------ #
                # Hypothesize Recommendation Criterion #
                # ------------------------------------ #
                rec_obj = NBRecommender(clue_obj)
                # ------------------------------- #
                # Update Recommendation Criterion #
                # ------------------------------- #
                updated_rec_obj = FunctionWordRemover(rec_obj)
                updated_rec_obj.report()
                # ------------------- #
                # Apply The Criterion #
                # ------------------- #
                scores = {}
                with rasengan.warn_ctm('Restricted Entities to 400'):
                    for e_idx, e in enumerate(EmSQ[:400] + Q):
                        try:
                            scores[e] = updated_rec_obj(url_mention[e])
                        except KeyError as e:
                            print >> sys.stderr, e
                            continue
                # ------------------- #
                # Measure Performance #
                # ------------------- #
                performance_aggregator(cat, scores, len(S), Q)
                continue
            continue
        continue
    # print performance_aggregator
    with open(args.report_pkl_fn, 'wb') as f:
        pkl.dump(performance_aggregator, f)


def read_report(report_pkl_fn):
    print pkl.load(open(report_pkl_fn))
    return


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--in_shelf', default='data/catpeople_clean_segmented_context.shelf', type=str)
    arg_parser.add_argument(
        '--fold_fn', default='data/cat-people-dev.fold.pkl', type=str)
    arg_parser.add_argument(
        '--cat2url_fn', default='data/cat-people-dev', type=str)
    arg_parser.add_argument(
        '--report_pkl_fn', default='data/performance_aggregator.pkl', type=str)
    arg_parser.add_argument('--evaluate', default=1, type=int)
    args = arg_parser.parse_args()
    with rasengan.warn_ctm('Using Rasengan Tokenizer'):
        # TOKENIZER = lambda x: x.split()
        TOKENIZER = rasengan.get_tokenizer()
    if args.evaluate:
        main()
    else:
        read_report(args.report_pkl_fn)
