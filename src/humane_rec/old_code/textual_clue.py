#!/usr/bin/env python
'''
| Filename    : textual_clue.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Sep 19 01:52:42 2016 (-0400)
| Last-Updated: Mon Sep 19 01:53:46 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
import catpeople_baseline_nb_config
import itertools
import rasengan


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
