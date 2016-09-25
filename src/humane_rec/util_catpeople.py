#!/usr/bin/env python
'''
| Filename    : util_catpeople.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Sep 19 01:51:46 2016 (-0400)
| Last-Updated: Sat Sep 24 18:55:48 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 32
'''
import os
from catpeople_preprocessor_config import PROJECT_PATH
import string
import rasengan

PRINTABLE = set(string.printable)
UNIVERSALDEP = ['acl',        # clausal modifier of noun (adjectival clause)
        'advcl',      # adverbial clause modifier
        'advmod',     # adverbial modifier
        'amod',       # adjectival modifier
        'appos',      # appositional modifier
        'aux',        # auxiliary
        'auxpass',    # passive auxiliary
        'case',       # case marking
        'cc',         # coordinating conjunction
        'ccomp',      # clausal complement
        'compound',   # compound
        'conj',       # conjunct
        'cop',        # copula
        'csubj',      # clausal subject
        'csubjpass',  # clausal passive subject
        'dep',        # unspecified dependency
        'det',        # determiner
        'discourse',  # discourse element
        'dislocated', # dislocated elements
        'dobj',       # direct object
        'expl',       # expletive
        'foreign',    # foreign words
        'goeswith',   # goes with
        'iobj',       # indirect object
        'list',       # list
        'mark',       # marker
        'mwe',        # multi-word expression
        'name',       # name
        'neg',        # negation modifier
        'nmod',       # nominal modifier
        'nsubj',      # nominal subject
        'nsubjpass',  # passive nominal subject
        'nummod',     # numeric modifier
        'parataxis',  # parataxis
        'punct',      # punctuation
        'remnant',    # remnant in ellipsis
        'reparandum', # overridden disfluency
        'root',       # root
        'vocative',   # vocative
        'xcomp',      # open clausal complement
]

# 3.5.2, this list contains 52 relations which is more than the 46 that
# syntaxnet can produce, but over is better than under for interning.
STANFORD_DEP = [
    'ROOT',       # root
    'nsubj',
    'csubj',
    'nsubjpass',
    'csubjpass',
    'dobj',
    'iobj',
    'ccomp',
    'xcomp',
    'acomp',

    'advmod',
    'advcl',
    'neg',

    'det',
    'amod',
    'appos',
    'num',
    'rcmod',
    'partmod',
    'infmod',
    'quantmod',

    'punct',
    'aux',
    'auxpass',
    'cop',

    'expl',
    'mark',
    'discourse',
    'dep',

    'prep',
    'pobj',
    'pcomp',

    'possessive',

    'nn',
    'number',
    'mwe',
    'goeswith',

    'conj',
    'cc',

    'parataxis',

    'npadvmod',
    'tmod',
    'predet',
    'preconj',
    'prt',
    'poss',
]


COARSE_TAGS = [
    '.',
    'ADJ',
    'ADP',
    'ADV',
    'CONJ',
    'DET',
    'NOUN',
    'NUM',
    'PRON',
    'PRT',
    'VERB',
    'X']

FINE_TAGS = [
    '-LRB-',
    '-RRB-',
    ',',
    '.',
    ':',
    'ADD',
    'AFX',
    'CC',
    'CD',
    'DT',
    'EX',
    'FW',
    'GW',
    'HYPH',
    'IN',
    'JJ',
    'JJR',
    'JJS',
    'LS',
    'MD',
    'NFP',
    'NN',
    'NNP',
    'NNPS',
    'NNS',
    'PDT',
    'POS',
    'PRP',
    'PRP$',
    'RB',
    'RBR',
    'RBS',
    'RP',
    'SYM',
    'TO',
    'UH',
    'VB',
    'VBD',
    'VBG',
    'VBN',
    'VBP',
    'VBZ',
    'WDT',
    'WP',
    'WP$',
    'WRB',
    '``',
    '\'\'',
    'X',
    'XX',
    '$',
    '#',
]
def get_labelmap():
    lmp = rasengan.TokenMapper(*STANFORD_DEP)
    lmp.finalize()
    return lmp

def get_coarse_tagmap():
    tmp = rasengan.TokenMapper(*COARSE_TAGS)
    tmp.finalize()
    return tmp

def get_fine_tagmap():
    tmp = rasengan.TokenMapper(*FINE_TAGS)
    tmp.finalize()
    return tmp

def load_cat2url(cat2url_fn):
    return dict((caturl_group[0].split()[0],
                 [e.strip().split()[1] for e in caturl_group])
                for caturl_group
                in rasengan.groupby(cat2url_fn,
                                    predicate=lambda x: x.split()[0]))
def remove_unprintable(s):
    return filter(lambda x: x in PRINTABLE, s)

def proj_open(path):
    for pfx in PROJECT_PATH:
        try:
            return open(os.path.join(os.path.expanduser(pfx), path), 'rb')
        except IOError:
            continue
    raise IOError(path)

def get_pfx():
    return PROJECT_PATH[0]


def get(l, idi):
    return [l[i] for i in idi]


def minus(E, S):
    S = set(S)
    return [e for e in E if e not in S]


def remove_unigrams(w, tmo, df_lim=None, df_obj=None):
    from rasengan.function_words import get_function_words
    bad_idx = []
    for e in get_function_words():
        e = e.lower()
        try:
            idx = tmo([e])[0]
            del w[idx]
            bad_idx.append(idx)
        except KeyError:
            continue
    if df_lim is not None:
        for idx in w.keys():
            if idx in df_obj and df_obj[idx] > df_lim:
                del w[idx]
                # print tmo[[idx]]
                bad_idx.append(idx)
    return w, bad_idx


def remove_bigrams(w, bad_idx):
    import catpeople_baseline_nb_config
    for index in w.keys():
        ct = index % catpeople_baseline_nb_config.MAX_TOK
        pt = ((index - ct) / catpeople_baseline_nb_config.MAX_TOK - 1)
        # Since remove unigrams already takes care of removing everything
        # that has high frequency therefore there is no need to remove
        # bigrams with high frequency separately.
        # or (df_lim is not None and index in df_obj and df_obj[index] > df_lim)
        if pt in bad_idx or ct in bad_idx:
            del w[index]
    return w


def color(f):
    assert 0 <= f <= 1
    return tuple([int(f * 7) * 32] * 3)
