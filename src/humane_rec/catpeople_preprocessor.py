#!/usr/bin/env python
'''
| Filename    : catpeople_preprocessor.py
| Description : Classes for Efficient Global Preprocessing of CatPeople Corpus
| Author      : Pushpendre Rastogi
| Created     : Thu Sep 22 18:03:09 2016 (-0400)
| Last-Updated: Sat Oct  1 19:53:53 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 250
'''
from catpeople_preprocessor_config import CONFIG, UNIGRAM, UNIVEC, \
    BIGRAM, BIVEC, DSCTOK, DSCSUF, DSCTOKVEC, UNISUF
from shelve import DbfilenameShelf
import gzip
import util_catpeople
import numpy as np
import sys
from joblib import Parallel, delayed
import functools
import itertools
import cPickle as pkl
import os
from collections import defaultdict
from scipy import io
from rasengan import csr_mat_builder
import rasengan
import argparse
import random

# ------- #
# GLOBALS #
# ------- #
CTnoun = None
CTverb = None
LMconj = None
LMdobj = None
LMpobj = None
LMprep = None
LMappos = None
LMacompnn = None
LMnnpa = None
LMpobjdobj = None
LMpobjpcomp = None
TM = None
LABELMAP = None
CTMAP = None
GENDER_TO_PRONOUN = None
TOKEN_TO_GENDER = None


def get_gender_to_pronoun(TM): # pylint: disable=redefined-outer-name
    return {0: set(TM(['him', 'his', 'he'])),
            1: set(TM(['she', 'her', 'hers']))}


def get_token_to_gender(TM): # pylint: disable=redefined-outer-name
    from rasengan.gender import GENDER
    TOKEN_TO_GENDER = {} # pylint: disable=redefined-outer-name
    for (t, v) in GENDER.iteritems():
        try:
            tid = TM([t.lower()])[0]
        except KeyError:
            continue
        else:
            TOKEN_TO_GENDER[tid] = v
    return TOKEN_TO_GENDER


def format_to_conll(lst):
    # LEMMA=CPOSTAG=POSTAG=FEATS=HEAD=DEPREL=PHEAD=PREPREL='_'
    s = '_\t_\t_\t_\t_\t_\t_\t_'
    return ''.join('%d\t%s\t%s\n' % (idx + 1, tok, s)
                   for idx, tok in enumerate(lst))


def print_to_conll(out_fn, catpeople, urls):
    ''' Print all mention sentences for all urls from catpeople to out_fn
    '''
    total_url = len(urls)
    print out_fn, total_url
    with gzip.open(out_fn, mode='wb') as out_f:
        for url_idx, url in enumerate(urls):
            if url_idx % 10000 == 0:
                print >> sys.stderr, 'DONE: %.3f' % (
                    float(url_idx * 100) / total_url)
            for mention in catpeople[url]:
                for sentence in mention[0]:
                    out_f.write(format_to_conll(TM[sentence]))
                    out_f.write('\n')
    return


def split(lst, parts):
    '''Split lst into parts. parts is an integer.
    '''
    l = len(lst)
    offset = 0
    jmp = l / parts
    for _ in range(parts - 1):
        yield lst[offset: offset + jmp]
        offset += jmp
    yield lst[offset:]


def arg_match(lst, elms):
    return [i for i in xrange(len(lst)) if lst[i] in elms]


def matching_pronouns(sentence, cts):
    ct = cts[0]
    try:
        gender = TOKEN_TO_GENDER[ct]
        elms = GENDER_TO_PRONOUN[gender]
        return arg_match(sentence, elms)
    except KeyError:
        return []


def catpeople_sentence_iterator(mentions, only_entity_bearer=False, yield_referents=False):
    ''' Yield the sentences related to cp[url] one by one.
    If told to yield only the entity bearing sentence from a mention then
    yield only one sentence from the mention.
    Params
    ------
    cp                 : The catpeople dataset
    url                : The URL
    only_entity_bearer : (default False)
    '''
    # Some of the mentions in the catpeople dataset are duplicates.
    mentions = rasengan.deduplicate_unhashables(mentions)
    # los_n_stuff = list of sentences and other markers.
    for los_n_stuff in mentions:
        cid = los_n_stuff[1]
        canonical_sentence = los_n_stuff[0][cid]
        e_range = range(los_n_stuff[2], los_n_stuff[3])
        canonical_tokens = [canonical_sentence[i] for i in e_range]
        if only_entity_bearer:
            if yield_referents:
                yield canonical_sentence, e_range
            else:
                yield canonical_sentence
        else:
            for idx, sentence in enumerate(los_n_stuff[0]):
                if yield_referents:
                    referents = arg_match(sentence, canonical_tokens)
                    if idx >= cid:
                        referents.extend(matching_pronouns(
                            sentence, canonical_tokens))
                    yield sentence, referents
                else:
                    yield sentence
    return


def yield_ngrams(n, sentence):
    ''' Yield Ngrams, not as tuples but as integers. In the worst case we yield
    really long integers that are upto len(TM)**3 + len(TM)**2 + len(TM)
    Params
    ------
    n        : The order of the $n$-grams
    sentence : The sentence.
    '''
    N = len(TM)
    if n == 0:
        for w in sentence:
            yield w
    elif n == 1:
        yield N * N + sentence[0]
        for i in range(1, len(sentence)):
            yield (1 + sentence[i - 1]) * N + sentence[i]
    elif n == 2:
        N2 = N * N
        yield N * N2 + N2 + sentence[0]
        if len(sentence) > 1:
            yield N * N2 + N * (1 + sentence[0]) + sentence[1]
            for i in range(2, len(sentence)):
                yield (1 + sentence[i - 2]) * N2 + (1 + sentence[i - 1]) * N + sentence[i]
    else:
        raise NotImplementedError(n)
    return

def yield_unisuf(sentence, parse):
    return ((l+1)*len(TM) + w for l,w in itertools.izip(parse, sentence))

def get_ngrams_from_catpeople_entity(n, mentions, cfg, PARSES, yield_nsuf=False):
    r = defaultdict(int)
    binarize_counts = cfg.binarize_counts
    for sentence in catpeople_sentence_iterator(mentions, cfg.only_entity_bearer):
        iterator = (yield_unisuf(sentence,
                                 PARSES[tuple(sentence)][1]) # PARSES[1] contains the roles
                    if yield_nsuf
                    else yield_ngrams(n, sentence))
        for w in iterator:
            if binarize_counts:
                r[w] = 1
            else:
                r[w] += 1
    return r


def get_width_for_bigrams():
    return len(TM) * (len(TM) + 1)

def get_width_for_unisuf():
    return len(TM) * (len(LABELMAP) + 1)

def entity_list_to_ngram_csr_mat(cfg, catpeople, width=None, n=0,
                                 add_governor_arc_label=False):
    assert n in [0, 1]
    url_list = catpeople['__URL_LIST__']
    shape = (len(url_list), len(TM) if width is None else width)
    PARSES = None
    if add_governor_arc_label:
        assert n == 0
        with rasengan.tictoc('Loading Parses'):  # 1 min
            PARSES = pkl.load(util_catpeople.proj_open(cfg.parsefn))
        iterator = (get_ngrams_from_catpeople_entity(n, catpeople[url], cfg,
                                                     PARSES, yield_nsuf=True)
                    for url_idx, url
                    in enumerate(url_list))
    else:
        iterator = (get_ngrams_from_catpeople_entity(n, catpeople[url], cfg, None)
                    for url_idx, url
                    in enumerate(url_list))
    return csr_mat_builder(iterator, shape=shape, verbose=0)


def get_valid_pfx(t, container):
    ''' Keep slicing prefixes of `t` till `t` is found in the container.
    Params
    ------
    t         : A string
    container : A container of strings.
    Returns
    -------
    A prefix of `t` that is guaranteed to be in `container`
    '''
    orig = t
    if t in container:
        return t
    # 1. Remove Unprintable Characters
    t = util_catpeople.remove_unprintable(t)
    if t in container:
        return t
    # 2. Convert some special `t` to their equivalents from the container.
    translate_table = {'(': 'lrb', ')': 'rrb'}
    if t in translate_table:
        tt = translate_table[t]
        assert tt in container
        return tt
    # 3. Prefix finding loop
    for _ in range(len(t) - 1):
        t = t[:-1]
        if t in container:
            return t
    raise ValueError((orig, t))


def substitute_unmappable_words(vectors):
    d = {}
    tvec = None
    for t, i in TM.t2i.iteritems():
        try:
            tvec = vectors[t]
        except KeyError:
            tvec = vectors[get_valid_pfx(t, vectors)]
        d[i] = tvec
    emb = np.empty((len(d), len(tvec)), dtype='float32')
    assert range(len(TM.t2i)) == sorted(TM.t2i.values())
    for i in xrange(len(TM.t2i)):
        emb[i] = d[i]
    del d
    return emb


def save_vec_file(input_fn, output_fn):
    if not os.path.exists(output_fn):
        vectors = pkl.load(util_catpeople.proj_open(input_fn))
        vectors = substitute_unmappable_words(vectors)
        np.save(open(output_fn, 'wb'), vectors, allow_pickle=False)
    else:
        print 'Skip Saving Vec file', output_fn
    return


def entity_descriptors(sentence, P, R, Tc, referents):
    '''
    Params
    ------
    sentence  :
    P         : The parents mention root as 0.
    R         :
    Tc        :
    referents : Rerefents are a pointer to the entity bearing words.
    '''
    ETS = referents
    B = {}
    D = {}
    Gpo1 = {}
    CONVERGED = False
    P = [_ - 1 for _ in P]
    while not CONVERGED:
        OLD_LEN_BD = len(B) + len(D) + len(Gpo1)  # +len(Gpo2)
        for i, (w, p, r, tc) in enumerate(itertools.izip(
                sentence, P, R, Tc)):
            if ((r == LMappos and p in ETS)
                or (r in LMacompnn and p in D)
                or (r in LMpobjpcomp and P[p] in D)
                or (r in LMpobjdobj and p in B)
                or (r == LMconj and P[p] in B and R[p] in LMpobjdobj)):
                D[i] = r
            if r in LMnnpa and i in ETS:
                D[p] = r
            if (r == LMdobj and Tc[p] == CTverb and p in D):
                B[p] = True
            if r == LMpobj and i in ETS and R[p] == LMprep and Tc[P[p]] == CTnoun:
                Gpo1[P[p]] = r
            # print TM[[sentence[_] for _ in B]], TM[[sentence[_] for _ in D]],
            # TM[[sentence[_] for _ in ETS]]
        NEW_LEN_BD = len(B) + len(D) + len(Gpo1)
        CONVERGED = (NEW_LEN_BD == OLD_LEN_BD)
        pass
    D.update(Gpo1)
    return D


def yield_dscfeat(sentence, parse, referents, yield_suf=False):
    N = len(TM)
    for idx, r in entity_descriptors(sentence, parse[0], parse[1], parse[2], referents).iteritems():
        s = sentence[idx]
        yield s
        if yield_suf:
            yield (r+1) * N + s
    return

def get_dscfeat_from_catpeople_entity(mentions, cfg, PARSES, yield_suf):
    r = defaultdict(int)
    binarize_counts = cfg.binarize_counts
    for sentence, referents in catpeople_sentence_iterator(
            mentions,
            only_entity_bearer=cfg.only_entity_bearer,
            yield_referents=True):
        for w in yield_dscfeat(sentence, PARSES[tuple(sentence)], referents,
                               yield_suf=yield_suf):
            if binarize_counts:
                r[w] = 1
            else:
                r[w] += 1
    return r


def entity_list_to_dscfeat_csr_mat(cfg, catpeople):
    url_list = catpeople['__URL_LIST__']
    yield_suf = cfg._name.startswith(DSCSUF)
    shape = (len(url_list), get_width_for_unisuf() if yield_suf else len(TM))
    with rasengan.tictoc('Loading Parses'):  # 1 min
        PARSES = pkl.load(util_catpeople.proj_open(cfg.parsefn))
    print 'Total Rows:', len(url_list)
    iterator = (get_dscfeat_from_catpeople_entity(catpeople[url], cfg, PARSES, yield_suf)
                for url in url_list)
    return csr_mat_builder(iterator, shape=shape, verbose=0)


def populate_dsctok_globals():
    global CTnoun
    global CTverb
    global LMconj
    global LMdobj
    global LMpobj
    global LMprep
    global LMappos
    global LMacompnn
    global LMnnpa
    global LMpobjdobj
    global LMpobjpcomp
    CTnoun = CTMAP(['NOUN'])[0]
    CTverb = CTMAP(['VERB'])[0]
    LMconj = LABELMAP(['conj'])[0]
    LMdobj = LABELMAP(['dobj'])[0]
    LMpobj = LABELMAP(['pobj'])[0]
    LMprep = LABELMAP(['prep'])[0]
    LMappos = LABELMAP(['appos'])[0]
    LMacompnn = LABELMAP(['acomp', 'nn'])
    LMnnpa = LABELMAP(['nsubj', 'nsubjpass', 'poss', 'advmod'])
    LMpobjdobj = LABELMAP(['pobj', 'dobj'])
    LMpobjpcomp = LABELMAP(['pobj', 'pcomp'])
    return


# --------------------------- #
# Functions For Each Modality #
# --------------------------- #
def doc_to_unigrams(cfg, catpeople):
    smat = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0)
    io.mmwrite(open(args.out_fn, 'wb'), smat)
    return

def doc_to_unisuf(cfg, catpeople):
    width = get_width_for_unisuf()
    smat0 = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0, width=width)
    smat1 = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0, width=width,
                                         add_governor_arc_label=True)
    io.mmwrite(open(args.out_fn, 'wb'), smat0 + smat1)
    return

def doc_to_bigrams(cfg, catpeople):
    width = get_width_for_bigrams()
    smat0 = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0, width=width)
    smat1 = entity_list_to_ngram_csr_mat(cfg, catpeople, n=1, width=width)
    io.mmwrite(open(args.out_fn, 'wb'), smat0 + smat1)
    return


def doc_to_bivec(cfg):
    '''Just touch the out_fn file'''
    open(args.out_fn, 'wb').close()
    return


def doc_to_univec(cfg, catpeople):
    save_vec_file(cfg.vecfn, args.out_fn + '.vec')
    out_fn = args.out_fn
    if not os.path.exists(out_fn):
        smat = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0)
        io.mmwrite(open(out_fn, 'wb'), smat)
    else:
        print 'Skip Saving Sparse Mat file', out_fn
    return


def doc_to_dscfeat(cfg, catpeople):
    populate_dsctok_globals()
    smat = entity_list_to_dscfeat_csr_mat(cfg, catpeople)
    io.mmwrite(open(args.out_fn, 'wb'), smat)
    return

def doc_to_dsctokvec(cfg):
    '''Just touch the out_fn file.
    There is no need to create new files.
    We can just reuse tokvec from old files.
    '''
    # save_vec_file(cfg.vecfn, args.out_fn + '.vec')
    open(args.out_fn, 'wb').close()
    return


def main():
    global TM
    global LABELMAP
    global CTMAP
    global GENDER_TO_PRONOUN
    global TOKEN_TO_GENDER
    cfg = CONFIG[args.config]
    catpeople = DbfilenameShelf(args.in_shelf, protocol=-1, flag='r')
    TM = catpeople['__TOKEN_MAPPER__']
    TM.finalize()
    LABELMAP = util_catpeople.get_labelmap()
    CTMAP = util_catpeople.get_coarse_tagmap()
    GENDER_TO_PRONOUN = get_gender_to_pronoun(TM)
    TOKEN_TO_GENDER = get_token_to_gender(TM)
    if args.print_to_conll:
        # Print CatPeople in Conll Format
        partial_print_to_conll = functools.partial(
            print_to_conll, catpeople=catpeople)
        n_jobs = 4
        Parallel(n_jobs=n_jobs)(
            delayed(partial_print_to_conll)(out_fn=out_fn, urls=urls)
            for (out_fn, urls)
            in itertools.izip(
                (args.out_fn + str(i) for i in range(n_jobs)),
                split(catpeople['__URL_LIST__'], n_jobs)))
        return
    else:
        name = cfg._name
        if name.startswith(UNIGRAM):
            return doc_to_unigrams(cfg, catpeople)
            # doc_to_unigrams
            # --> entity_list_to_ngram_csr_mat(n=0, width=None)
            #     --> get_ngrams_from_catpeople_entity
            #         --> yield_ngrams
            #         --> catpeople_sentence_iterator
        elif name.startswith(BIGRAM):
            return doc_to_bigrams(cfg, catpeople)
            # doc_to_unigrams
            # --> entity_list_to_ngram_csr_mat(n=0, width=None)
            # --> get_width_for_bigrams
            # --> entity_list_to_ngram_csr_mat(n=1, width=width)
        elif name.startswith(UNIVEC):
            return doc_to_univec(cfg, catpeople)
            # doc_to_univec
            # --> save_vec_file
            # --> entity_list_to_ngram_csr_mat(n=0, width=None)
        elif name.startswith(BIVEC):
            return doc_to_bivec(cfg)
        elif name.startswith(DSCTOK) or name.startswith(DSCSUF):
            return doc_to_dscfeat(cfg, catpeople)
            # --> entity_list_to_dscfeat_csr_mat
            #     --> get_dscfeat_from_catpeople_entity
            #         --> catpeople_sentence_iterator
            #         --> yield_dsctok
        elif name.startswith(DSCTOKVEC):
            return doc_to_dsctokvec(cfg)
        elif name.startswith(UNISUF):
            return doc_to_unisuf(cfg, catpeople)
        else:
            raise NotImplementedError(name)


if __name__ == '__main__':
    PFX = util_catpeople.get_pfx()
    arg_parser = argparse.ArgumentParser(
        description='Globally Preprocess the CatPeople Corpus')
    arg_parser.add_argument('--seed', default=0, type=int)
    arg_parser.add_argument(
        '--in_shelf', type=str,
        default=(PFX + '/catpeople_clean_segmented_context.shelf'))
    arg_parser.add_argument('--config', default=0, type=int)
    arg_parser.add_argument('--print_to_conll', default=None, type=str)
    arg_parser.add_argument('--out_fn', default=None, type=str)
    args = arg_parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    if args.out_fn is None:
        if args.print_to_conll:
            args.out_fn = PFX + '/catpeople.conll.gz'
        else:
            args.out_fn = '%s/catpeople_pp_%d' % (PFX, args.config)
    main()
