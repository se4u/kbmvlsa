#!/usr/bin/env python
'''
| Filename    : util_catpeople.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Sep 19 01:51:46 2016 (-0400)
| Last-Updated: Thu Sep 29 21:51:58 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 39
'''
import os
from catpeople_preprocessor_config import PROJECT_PATH
import string
import rasengan
import scipy.sparse
import itertools

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


# def remove_bigrams(w, bad_idx):
#     import catpeople_baseline_nb_config
#     for index in w.keys():
#         ct = index % catpeople_baseline_nb_config.MAX_TOK
#         pt = ((index - ct) / catpeople_baseline_nb_config.MAX_TOK - 1)
#         # Since remove unigrams already takes care of removing everything
#         # that has high frequency therefore there is no need to remove
#         # bigrams with high frequency separately.
#         # or (df_lim is not None and index in df_obj and df_obj[index] > df_lim)
#         if pt in bad_idx or ct in bad_idx:
#             del w[index]
#     return w


def color(f):
    assert 0 <= f <= 1
    return tuple([int(f * 7) * 32] * 3)


def patch_scipy(scipy):
    if scipy.__version__ in ("0.14.0", "0.14.1", "0.15.1"):
        _get_index_dtype = scipy.sparse.sputils.get_index_dtype
        def _my_get_index_dtype(*a, **kw):
            kw.pop('check_contents', None)
            return _get_index_dtype(*a, **kw)
        scipy.sparse.compressed.get_index_dtype = _my_get_index_dtype
        scipy.sparse.csr.get_index_dtype = _my_get_index_dtype
        scipy.sparse.bsr.get_index_dtype = _my_get_index_dtype

def set_column_of_sparse_matrix_to_zero(smat, col_idi):
    if smat.shape[1] < 1e7:
        if not scipy.sparse.isspmatrix_csc(smat):
            smat = smat.tocsc()
        for col_idx in col_idi:
            smat.data[smat.indptr[col_idx]:smat.indptr[col_idx+1]] = 0
        smat.eliminate_zeros()
        return smat
    else:
        assert scipy.sparse.isspmatrix_coo(smat)
        if not isinstance(col_idi, set):
            col_idi = set(col_idi)
        R, C, V = [], [], []
        for idx in xrange(len(smat.col)):
            if smat.col[idx] not in col_idi:
                R.append(smat.row[idx])
                C.append(smat.col[idx])
                V.append(smat.data[idx])
        smat = scipy.sparse.coo_matrix((V, (R,C)), shape=smat.shape, dtype=smat.dtype)
        smat.sum_duplicates()
        return smat


def index_coo_mat(mat, idi, axis=0):
    ''' Index a matrix using the list of indices `idi`.
    The axis parameter tells us whether the idi refer to
    columns on rows. By default they refer to rows.
    --- INPUT ---
    mat  : A sparse COO matrix.
    idi  : A list of integers
    axis : `idi` refers to axis=axis (default 0)
    --- OUTPUT ---
    A new sparse COO matrix which is a submatrix of the original.
    '''
    assert axis in [0,1]
    idi_ = {}
    for i,e in enumerate(idi):
        idi_[e]=i
    idi = idi_
    R, C, V = [], [], []
    for e in itertools.izip(mat.row, mat.col, mat.data):
        if e[axis] in idi:
            R.append(idi[e[0]] if axis == 0 else e[0])
            C.append(idi[e[1]] if axis == 1 else e[1])
            V.append(e[2])
    mat = scipy.sparse.coo_matrix(
        (V, (R,C)),
        shape=((len(idi), mat.shape[1]) if axis == 0 else (mat.shape[0], len(idi))),
        dtype=mat.dtype)
    mat.sum_duplicates()
    return mat
