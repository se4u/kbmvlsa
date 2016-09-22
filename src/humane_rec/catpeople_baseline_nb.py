#!/usr/bin/env python
'''
| Filename    : catpeople_baseline_nb.py
| Description : The Baseline NB experiment.
| Author      : Pushpendre Rastogi
| Created     : Sun Sep  4 18:32:35 2016 (-0400)
| Last-Updated: Thu Sep 22 00:07:21 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 343
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
from collections import defaultdict
from performance_aggregator import Performance_Aggregator
import catpeople_baseline_nb_config
from textual_clue import TextualClueObject
from util_catpeople import get, minus, remove_unigrams, remove_bigrams, color
from fabulous.color import fg256


class NBRecommender(object):

    def __init__(self, clue_obj):
        self.clue_obj = clue_obj
        self.w = {}
        for feat in fS:
            self.w[feat] = None

    def __call__(self, Se):
        w = self.w
        cn = self.clue_obj.create_ngrams
        return sum(w[feat]
                   for n in [1, 2]
                   for feat in cn(Se, n)
                   if feat in w)


class FunctionWordRemover(object):

    def __init__(self, rec_obj,
                 ngram_occurrence,
                 remove_bigram=True,
                 limit_features=0,
                 df_lim=None,
                 df_obj=None,
                 alpha=1):
        self.rec_obj = rec_obj
        w = dict(rec_obj.w) # COPY
        clue_obj = rec_obj.clue_obj
        S = clue_obj.S
        fS = clue_obj.fS
        wprime_thresh = ngram_occurrence * len(S)
        tmo = rec_obj.clue_obj.tmo

        # -------------------- #
        # First Remove N-grams #
        # -------------------- #
        new_w, bad_idx = remove_unigrams(w, tmo, df_lim, df_obj)
        if remove_bigram:
            new_w = remove_bigrams(new_w, bad_idx)

        # Now remove features that don't occur often enough.
        for feat in new_w.keys():
            wprime = (sum(1 for e in S if feat in clue_obj.features[e])
                      / self.alpha)
            if wprime > wprime_thresh:
                w[feat] = log(1 + wprime)

        print 'FunctionWordRemover', len(w)
        self.w = w
        self.df_lim = df_lim
        self.df_obj = df_obj
        self.min_df = (None
                       if df_obj is None
                       else min(df_obj.itervalues()))
        if limit_features:
            good_feat = set(
                sorted(self.w.iterkeys(),
                       key=lambda x: self.w[x],
                       reverse=True)[:limit_features])

    def __call__(self, Se, ename=''):
        cn = self.rec_obj.clue_obj.create_ngrams
        w = self.w
        df_obj = self.df_obj
        min_df = self.min_df
        predicate = lambda x: x in w
        features = cn(Se, 12, predicate=predicate) # Read 12 as One Two
        val = sum(w[feat] for feat in features)
        val2 = sum( w[feat] / log(df_obj[feat] if feat in df_obj else min_df)
                   for feat in features)
        # print ename, self.rec_obj.clue_obj.tmo[features.keys()], val
        return val

    def report(self, limit=20):
        print 'Total Features', len(self.w)
        for idx, (a, b) in enumerate(
                sorted(self.w.iteritems(), key=lambda x: x[1], reverse=True)):
            if idx < limit:
                print (self.rec_obj.clue_obj.tmo[a], b)


def update_shelf():
    url_mention = DbfilenameShelf(args.in_shelf, protocol=-1)
    TM = url_mention['__TOKEN_MAPPER__']
    TM.finalize(catpeople_baseline_nb_config.MAX_TOK)
    E = url_mention['__URL_LIST__']
    n_doc = 10000
    with rasengan.tictoc('Extracting Contexts'):
        df_obj = TextualClueObject(E[:n_doc], url_mention, TM)
    df = defaultdict(int)
    for features in df_obj.features.itervalues():
        for f in features:
            df[f] += 1
    for f in df.keys():
        df[f] = df[f] / float(n_doc)
    url_mention['__DF__'] = dict(df)
    url_mention.close()
    return


def setup():
    ''' Load the catpeople data.
    '''
    url_mention = DbfilenameShelf(args.in_shelf, protocol=-1, flag='r')
    TM = url_mention['__TOKEN_MAPPER__']
    TM.finalize(catpeople_baseline_nb_config.MAX_TOK)
    E = url_mention['__URL_LIST__']
    DF = url_mention['__DF__']
    cat_folds = pkl.load(open(args.fold_fn))
    cat2url = dict((caturl_group[0].split()[0],
                    [e.strip().split()[1] for e in caturl_group])
                   for caturl_group
                   in rasengan.groupby(args.cat2url_fn,
                                       predicate=lambda x: x.split()[0]))
    performance_aggregator = Performance_Aggregator(args=args)
    return (url_mention, TM, E, cat_folds, cat2url, performance_aggregator, DF)


def show_mentions_of_person():
    ''' show all the mentions that a particular person appears in.
    '''
    (url_mention, TM, E, cat_folds, cat2url, performance_aggregator, _) = setup()
    mentions = url_mention[args.single_person]
    idx = 0
    for mention in mentions:
        sentences = mention[0]
        for sentence in sentences:
            print idx, ' '.join(TM[sentence])
            idx += 1


def show_step3_features():
    ''' Show the selected features
    '''
    (url_mention, TM, E, cat_folds, cat2url, performance_aggregator, DF) = setup()
    for cat_idx, (cat, folds) in enumerate(cat_folds.items()):
        train_idx, test_idx = folds[0]
        S = get(cat2url[cat], train_idx)
        clue_obj = TextualClueObject(S, url_mention, TM)
        tmo = clue_obj.tmo
        features = clue_obj.features
        c = defaultdict(int)
        for e, feat in features.iteritems():
            feat, bad_idx = remove_unigrams(feat, tmo, df_lim=args.df_lim, df_obj=DF)
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


def catpeople_stats():
    ''' Show Statistics about the CatPeople Dataset
    '''
    (url_mention, TM, E, cat_folds, cat2url,
     performance_aggregator, _) = setup()
    print 'Total Number of entities', len(E)
    print 'Total Number of Categories', len(cat2url)
    print 'Total Number of URLs', len(set(rasengan.flatten(cat2url.itervalues())))
    print 'Total Number of mentions', sum(len(url_mention[e]) for e in E)
    return



def evaluate_impl(url_mention, TM, E, cat_folds, cat2url,
                  performance_aggregator, DF, cat_idx, cat, folds):
    print >> sys.stderr, 'progress = %.2f\r' % (
            float(cat_idx) / len(cat_folds)),
    for (train_idx, test_idx) in folds:
        for train_set_size in [1]:  # 0.5
            S = get(cat2url[cat],
                    train_idx[:int(len(train_idx) * train_set_size)])
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
            rec_obj = NBRecommender(clue_obj, args.ngram_occurrence)
            # ------------------------------- #
            # Update Recommendation Criterion #
            # ------------------------------- #
            updated_rec_obj = FunctionWordRemover(
                rec_obj, df_obj=DF, df_lim=args.df_lim)
            updated_rec_obj.report()
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

def evaluate():
    from joblib import Parallel, delayed
    (url_mention, TM, E, cat_folds, cat2url, performance_aggregator, DF) = setup()
    Parallel(n_jobs=32)(
        delayed(evaluate_impl)(
            url_mention, TM, E, cat_folds, cat2url,
            performance_aggregator, DF, cat_idx, cat, folds)
        for cat_idx, (cat, folds) in enumerate(cat_folds.items()))
    with open(args.report_pkl_fn, 'wb') as f:
        pkl.dump(performance_aggregator, f)


def read_report(report_pkl_fn):
    ''' The main reporting function
    '''
    perf_obj = pkl.load(open(report_pkl_fn))
    try:
        print perf_obj.args.ngram_occurrence
    except AttributeError:
        pass
    for e in (perf_obj.fold_stats(add_cat=True)):
        print e
    print perf_obj
    return


def main():
    global args
    import os
    PFX = ('/export/b15/prastog3'
           if os.uname()[1] == 'b15'
           else 'data')
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument(
        '--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--in_shelf', default='%s/catpeople_clean_segmented_context.shelf'%PFX, type=str)
    arg_parser.add_argument(
        '--fold_fn', default='data/cat-people-dev.fold.pkl', type=str)
    arg_parser.add_argument(
        '--cat2url_fn', default='data/cat-people-dev', type=str)
    arg_parser.add_argument(
        '--report_pkl_fn', default='data/performance_aggregator.pkl', type=str)
    arg_parser.add_argument('--evaluate', default=1, type=int)
    arg_parser.add_argument('--single_person', default=None, type=str)
    arg_parser.add_argument('--show_step3_features', default=None, type=int)
    arg_parser.add_argument('--ngram_occurrence', default=0.7, type=float)
    arg_parser.add_argument('--catpeople_stats', default=0, type=int)
    arg_parser.add_argument('--update_shelf', default=0, type=int)
    arg_parser.add_argument('--df_lim', default=None, type=float)
    args = arg_parser.parse_args()
    with rasengan.warn_ctm('Using Rasengan Tokenizer'):
        # TOKENIZER = lambda x: x.split()
        TOKENIZER = rasengan.get_tokenizer()
    if args.evaluate:
        evaluate()
    if args.single_person:
        show_mentions_of_person()
        return
    if args.show_step3_features:
        show_step3_features()
        return
    if args.catpeople_stats:
        catpeople_stats()
        return
    if args.update_shelf:
        update_shelf()
        return
    read_report(args.report_pkl_fn)

if __name__ == '__main__':
    args = None
    main()
