#!/usr/bin/env python
'''
| Filename    : catpeople_baseline_nb.py
| Description : The Baseline NB experiment.
| Author      : Pushpendre Rastogi
| Created     : Sun Sep  4 18:32:35 2016 (-0400)
| Last-Updated: Sun Sep 11 21:06:48 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 269
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
from rasengan.function_words import get_function_words


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
                 alpha=1,
                 ngram_occurrence=0.7):
        self.clue_obj = clue_obj
        self.w = {}
        self.alpha = alpha
        wprime_thresh = ngram_occurrence * len(clue_obj.S)
        for feat in clue_obj.fS:
            wprime = (sum(1 for e in clue_obj.S if feat in clue_obj.features[e])
                      / self.alpha)
            if (ngram_occurrence != 0) or (wprime > wprime_thresh):
                self.w[feat] = log(1 + wprime)

    def __call__(self, Se):
        w = self.w
        cn = self.clue_obj.create_ngrams
        return sum(w[feat]
                   for n in [1, 2]
                   for feat in cn(Se, n)
                   if feat in w)


def remove_unigrams(w, tmo):
    bad_idx = []
    for e in get_function_words():
        e = e.lower()
        try:
            idx = tmo([e])[0]
            del w[idx]
            bad_idx.append(idx)
        except KeyError:
            continue
    return w, bad_idx


def remove_bigrams(w, bad_idx):
    for index in w.keys():
        ct = index % catpeople_baseline_nb_config.MAX_TOK
        pt = ((index - ct) / catpeople_baseline_nb_config.MAX_TOK - 1)
        if pt in bad_idx or ct in bad_idx:
            del w[index]
    return w


class FunctionWordRemover(object):

    def __init__(self, rec_obj, remove_bigram=True, limit_features=0, hack_features=False):
        self.rec_obj = rec_obj
        self.w = dict(rec_obj.w)
        tmo = rec_obj.clue_obj.tmo
        self.w, bad_idx = remove_unigrams(self.w, tmo)
        if remove_bigram:
            self.w = remove_bigrams(self.w, bad_idx)
        if limit_features:
            good_feat = set(
                sorted(self.w.iterkeys(), key=lambda x: self.w[x], reverse=True)[:limit_features])

        if hack_features:
            rasengan.warn('Hacking the features')
            good_feat = set(
                self.rec_obj.clue_obj.tmo([ee])[0] for ee in ['emigrant', 'emigrate', 'india', 'british', 'indian', 'london'])
            for feat in self.w.keys():
                if feat not in good_feat:
                    del self.w[feat]

    def __call__(self, Se, ename=''):
        cn = self.rec_obj.clue_obj.create_ngrams
        w = self.w
        predicate = lambda x: x in w
        features = cn(Se, 12, predicate=predicate)
        val = sum(w[feat] for feat in features)
        # print ename, self.rec_obj.clue_obj.tmo[features.keys()], val
        return val

    def report(self, limit=20):
        print 'Total Features', len(self.w)
        for idx, (a, b) in enumerate(
                sorted(self.w.iteritems(), key=lambda x: x[1], reverse=True)):
            if idx < limit:
                print (self.rec_obj.clue_obj.tmo[a], b)


class Performance_Aggregator(object):

    def __init__(self, args=None):
        self.record = defaultdict(list)
        self.args = args

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

    def get_fold_stats(self, fold):
        arr = [0] * len(fold[1])
        for _, i in fold[2]:
            arr[i] = 1
        ap = average_precision(arr)
        p_at_10 = float(sum(arr[:10]))
        p_at_100 = float(sum(arr[:100]))
        random.shuffle(arr)
        rap = average_precision(arr)
        rp_at_10 = float(sum(arr[:10]))
        rp_at_100 = float(sum(arr[:100]))
        return [ap, rap, p_at_10, rp_at_10, p_at_100, rp_at_100]

    def report_fold(self, cat, fold, S_size=-1):
        [ap, rap, p_at_10, rp_at_10, p_at_100,
            rp_at_100] = self.get_fold_stats(fold)
        return '%-40s(Training=%-3d,needles=%-3d,haystack=%-3d) (AUPR %.3f %.3f) (P@10 %d %d) (P@100 %d %d)' % (
            cat, S_size, len(fold[0]), len(fold[1]), ap, rap, p_at_10, rp_at_10, p_at_100, rp_at_100)

    def __str__(self):
        fold_stats = [self.get_fold_stats(fold)
                      for cat in self.record
                      for fold in self.record[cat]]
        [ap, rap, p_at_10, rp_at_10, p_at_100, rp_at_100] = np.array(
            fold_stats).mean(axis=0).tolist()
        return '(AUPR %.3f %.3f) (P@10 %.3f %.3f) (P@100 %.3f %.3f)' % (
            ap, rap, p_at_10, rp_at_10, p_at_100, rp_at_100)


def setup():
    url_mention = DbfilenameShelf(args.in_shelf, protocol=-1, flag='r')
    TM = url_mention['__TOKEN_MAPPER__']
    TM.finalize(catpeople_baseline_nb_config.MAX_TOK)
    E = url_mention['__URL_LIST__']
    cat_folds = pkl.load(open(args.fold_fn))
    cat2url = dict((caturl_group[0].split()[0], [e.strip().split()[1] for e in caturl_group])
                   for caturl_group
                   in rasengan.groupby(args.cat2url_fn, predicate=lambda x: x.split()[0]))
    performance_aggregator = Performance_Aggregator(args=args)
    return (url_mention, TM, E, cat_folds, cat2url, performance_aggregator)


def show():
    (url_mention, TM, E, cat_folds, cat2url, performance_aggregator) = setup()
    mentions = url_mention[args.single_person]
    idx = 0
    for mention in mentions:
        sentences = mention[0]
        for sentence in sentences:
            print idx, ' '.join(TM[sentence])
            idx += 1

from fabulous.color import fg256


def color(f):
    assert 0 <= f <= 1
    return tuple([int(f * 7) * 32] * 3)


def diverse_categories():
    (url_mention, TM, E, cat_folds, cat2url, performance_aggregator) = setup()
    for cat_idx, (cat, folds) in enumerate(cat_folds.items()):
        train_idx, test_idx = folds[0]
        S = get(cat2url[cat], train_idx)
        clue_obj = TextualClueObject(S, url_mention, TM)
        tmo = clue_obj.tmo
        features = clue_obj.features
        c = defaultdict(int)
        for e, feat in features.iteritems():
            feat, bad_idx = remove_unigrams(feat, tmo)
            feat = remove_bigrams(feat, bad_idx)
            for f in feat:
                c[f] += 1
        # if e[1] > len(features) * 2.0 / 4.0
        common_feat = sorted(
            c.iteritems(), key=lambda x: x[1], reverse=True)[:20]
        total = float(len(S))
        if len(common_feat) == 0:
            print 'Diverse:', '%-35s' % cat[:35], fg256('red', '|||'),
        else:
            print 'Common: ', '%-35s' % cat[:35], fg256('red', '|||'),
            for e in common_feat:
                print fg256(color((1 - e[1] / total) / 1.2), tmo[[e[0]]][0]),
            print
    import pdb
    pdb.set_trace()


def eval():
    (url_mention, TM, E, cat_folds, cat2url, performance_aggregator) = setup()
    # rasengan.warn('Using Reduced number of categories and folds')
    for cat_idx, (cat, folds) in enumerate(cat_folds.items()):
        print >> sys.stderr, 'progress = %.2f\r' % (
            float(cat_idx) / len(cat_folds)),
        for (train_idx, test_idx) in folds:
            for train_set_size in [1]:  # 0.5
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
                rec_obj = NBRecommender(
                    clue_obj, ngram_occurrence=args.ngram_occurrence)
                # ------------------------------- #
                # Update Recommendation Criterion #
                # ------------------------------- #
                updated_rec_obj = FunctionWordRemover(rec_obj)
                # updated_rec_obj.report()
                # ------------------- #
                # Apply The Criterion #
                # ------------------- #
                scores = {}
                rasengan.warn('Restricted Entities to 1000')
                for e_idx, e in enumerate(EmSQ[:1000] + Q):
                    try:
                        scores[e] = updated_rec_obj(url_mention[e], ename=e)
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


def main():
    global args
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument(
        '--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--in_shelf', default='data/catpeople_clean_segmented_context.shelf', type=str)
    arg_parser.add_argument(
        '--fold_fn', default='data/cat-people-dev.fold.pkl', type=str)
    arg_parser.add_argument(
        '--cat2url_fn', default='data/cat-people-dev', type=str)
    arg_parser.add_argument(
        '--report_pkl_fn', default='data/performance_aggregator.pkl', type=str)
    arg_parser.add_argument('--evaluate', default=1, type=int)
    arg_parser.add_argument('--single_person', default=None, type=str)
    arg_parser.add_argument('--diverse_categories', default=None, type=int)
    arg_parser.add_argument('--ngram_occurrence', default=0.7, type=float)
    args = arg_parser.parse_args()
    with rasengan.warn_ctm('Using Rasengan Tokenizer'):
        # TOKENIZER = lambda x: x.split()
        TOKENIZER = rasengan.get_tokenizer()
    if args.evaluate:
        eval()
    if args.single_person:
        show()
        return
    if args.diverse_categories:
        diverse_categories()
        return
    read_report(args.report_pkl_fn)

if __name__ == '__main__':
    args = None
    main()
