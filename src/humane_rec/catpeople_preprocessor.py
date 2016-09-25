#!/usr/bin/env python
'''
| Filename    : catpeople_preprocessor.py
| Description : Classes for Efficient Global Preprocessing of CatPeople Corpus
| Author      : Pushpendre Rastogi
| Created     : Thu Sep 22 18:03:09 2016 (-0400)
| Last-Updated: Sun Sep 25 02:07:27 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 212
'''
from catpeople_preprocessor_config import CONFIG, UNIGRAM, UNIVEC, \
    BIGRAM, BIVEC, DSCTOK, DSCSUF, DSCTOKVEC
from shelve import DbfilenameShelf
import gzip
import util_catpeople
import numpy as np
import sys
from joblib import Parallel, delayed
import functools, itertools
import cPickle as pkl
import os
from collections import defaultdict
from scipy import io
from rasengan import tictoc, csr_mat_builder, groupby
import rasengan
import argparse
import random

def format_to_conll(lst):
    # LEMMA=CPOSTAG=POSTAG=FEATS=HEAD=DEPREL=PHEAD=PREPREL='_'
    s = '_\t_\t_\t_\t_\t_\t_\t_'
    return ''.join('%d\t%s\t%s\n'%(idx+1, tok, s)
                   for idx, tok in enumerate(lst))

def print_to_conll(out_fn, catpeople, urls):
    total_url = len(urls)
    print out_fn, total_url
    with gzip.open(out_fn, mode='wb') as out_f:
        for url_idx, url in enumerate(urls):
            if url_idx % 10000 == 0:
                print >> sys.stderr, 'DONE: %.3f'%(float(url_idx*100)/total_url)
            for mention in catpeople[url]:
                for sentence in mention[0]:
                    out_f.write(format_to_conll(TM[sentence]))
                    out_f.write('\n')
    return

def split(lst, parts):
    l = len(lst)
    offset = 0
    jmp = l / parts
    for _ in range(parts-1):
        yield lst[offset: offset+jmp]
        offset+=jmp
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
                        referents.extend(matching_pronouns(sentence, canonical_tokens))
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
            yield (1 + sentence[i-1]) * N +  sentence[i]
    elif n == 2:
        N2 = N*N
        yield N*N2 + N2 +sentence[0]
        if len(sentence) > 1:
            yield N*N2 + N*(1+sentence[0]) + sentence[1]
            for i in range(2, len(sentence)):
                yield (1+sentence[i-2])*N2 + (1+sentence[i-1])*N + sentence[i]
    else:
        raise NotImplementedError(n)
    return


def get_ngrams_from_catpeople_entity(n, mentions, cfg):
    r = defaultdict(int)
    binarize_counts = cfg.binarize_counts
    for sentence in catpeople_sentence_iterator(mentions, cfg.only_entity_bearer):
        for w in yield_ngrams(n, sentence):
            if binarize_counts:
                r[w] = 1
            else:
                r[w] += 1
    return r

def get_width_for_bigrams():
    return len(TM)*(len(TM) + 1)


def entity_list_to_ngram_csr_mat(cfg, catpeople, width=None, n=0):
    assert n in [0, 1]
    url_list = catpeople['__URL_LIST__']
    shape = (len(url_list), len(TM) if width is None else width)
    return csr_mat_builder(
        (get_ngrams_from_catpeople_entity(n, catpeople[url], cfg)
         for url_idx, url
         in enumerate(url_list)),
        shape=shape,
        verbose=1000)

def get_valid_pfx(t, container):
    orig = t
    t = util_catpeople.remove_unprintable(t)
    translate_table = {'(': 'lrb', ')': 'rrb'}
    if t in container:
        return t
    if t in translate_table:
        tt = translate_table[t]
        assert tt in container
        return tt
    for _ in range(len(t)-1):
        t = t[:-1]
        if t in container:
            return t
    raise ValueError((orig, t))

def substitute_unmappable_words(vectors):
    d = {}
    tvec = None
    for t,i in TM.t2i.iteritems():
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

def save_vec_file(vecfn, out_fn):
    # This takes only a second !!
    vectors = pkl.load(util_catpeople.proj_open(vecfn))
    vectors = substitute_unmappable_words(vectors)
    np.save(open(out_fn, 'wb'), vectors, allow_pickle=False)
    return

def doc_to_unigrams(cfg, catpeople):
    smat = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0)
    io.mmwrite(open(args.out_fn, 'wb'), smat) # 51.8s
    return

def doc_to_bigrams(cfg, catpeople):
    width = get_width_for_bigrams()
    smat0 = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0, width=width)
    smat1 = entity_list_to_ngram_csr_mat(cfg, catpeople, n=1, width=width)
    io.mmwrite(open(args.out_fn, 'wb'), smat0 + smat1) # 51.8s
    return

def doc_to_univec(cfg, catpeople):
    out_fn = args.out_fn + '.vec'
    if not os.path.exists(out_fn):
        save_vec_file(cfg.vecfn, out_fn)
    else:
        print 'Skip Saving Vec file', out_fn

    out_fn = args.out_fn
    if not os.path.exists(out_fn):
        smat = entity_list_to_ngram_csr_mat(cfg, catpeople, n=0) # 36.7s
        io.mmwrite(open(out_fn, 'wb'), smat) # 51.8s
    else:
        print 'Skip Saving Sparse Mat file', out_fn
    return

#
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
    Gpo2 = {}
    CONVERGED = False
    P = [_-1 for _ in P]
    while not CONVERGED:
        OLD_LEN_BD = len(B) + len(D) + len(Gpo1) # +len(Gpo2)
        for i, (w, p, r, tc) in enumerate(itertools.izip(
                sentence, P, R, Tc)):
            if ((r == LMappos and p in ETS )
                or (r in LMacompnn and p in D)
                or (r in LMpobjpcomp and P[p] in D)
                or (r in LMpobjdobj and p in B )
                or (r == LMconj and P[p] in B and R[p] in LMpobjdobj)):
                D[i] = True
            if r in LMnnpa and i in ETS:
                D[p] = True
            if (r == LMdobj and Tc[p] == CTverb and p in D):
                B[p] = True
            if r == LMpobj and i in ETS and R[p] == LMprep and Tc[P[p]] == CTnoun:
                Gpo1[P[p]] = True
            # print TM[[sentence[_] for _ in B]], TM[[sentence[_] for _ in D]], TM[[sentence[_] for _ in ETS]]
        NEW_LEN_BD = len(B) + len(D) + len(Gpo1) # + len(Gpo2)
        CONVERGED = (NEW_LEN_BD == OLD_LEN_BD)
        pass
    D.update(Gpo1)
    D.update(Gpo2)
    return D


def yield_dsctok(sentence, parse, referents):
    return [sentence[_]
            for _
            in entity_descriptors(sentence,
                                  parse[0],
                                  parse[1],
                                  parse[2],
                                  referents)]

def get_dsctok_from_catpeople_entity(mentions, cfg, PARSES):
    r = defaultdict(int)
    binarize_counts = cfg.binarize_counts
    for sentence, referents in catpeople_sentence_iterator(
            mentions,
            only_entity_bearer=cfg.only_entity_bearer,
            yield_referents=True):
        parse = PARSES[tuple(sentence)]
        for w in yield_dsctok(sentence, parse, referents):
            if binarize_counts:
                r[w] = 1
            else:
                r[w] += 1
    return r

def entity_list_to_dsctok_csr_mat(cfg, catpeople):
    url_list = catpeople['__URL_LIST__']
    shape = (len(url_list), len(TM))
    labelmap = util_catpeople.get_labelmap()
    with rasengan.tictoc('Loading Parses'): # 1 min
        PARSES = pkl.load(util_catpeople.proj_open(cfg.parsefn))
    print 'Total Rows:', len(url_list)
    return csr_mat_builder((get_dsctok_from_catpeople_entity(catpeople[url], cfg, PARSES)
                            for url
                            in url_list),
                           shape=shape,
                           verbose=1000)

def doc_to_dsctok(cfg, catpeople):
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
    CTnoun=CTMAP(['NOUN'])[0]
    CTverb=CTMAP(['VERB'])[0]
    LMconj=LABELMAP(['conj'])[0]
    LMdobj=LABELMAP(['dobj'])[0]
    LMpobj=LABELMAP(['pobj'])[0]
    LMprep=LABELMAP(['prep'])[0]
    LMappos=LABELMAP(['appos'])[0]
    LMacompnn=LABELMAP(['acomp', 'nn'])
    LMnnpa=LABELMAP(['nsubj', 'nsubjpass', 'poss', 'advmod'])
    LMpobjdobj=LABELMAP(['pobj', 'dobj'])
    LMpobjpcomp=LABELMAP(['pobj', 'pcomp'])

    smat = entity_list_to_dsctok_csr_mat(cfg, catpeople)
    io.mmwrite(open(args.out_fn, 'wb'), smat) # 51.8s
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
    GENDER_TO_PRONOUN = {0:set(TM(['him', 'his', 'he'])),
                         1:set(TM(['she', 'her', 'hers']))}
    from rasengan.gender import GENDER
    TOKEN_TO_GENDER = {}
    for (t,v) in GENDER.iteritems():
        try:
            tid = TM([t.lower()])[0]
        except KeyError:
            continue
        else:
            TOKEN_TO_GENDER[tid] = v

    if args.print_to_conll:
        # Print CatPeople in Conll Format
        partial_print_to_conll = functools.partial(print_to_conll, catpeople=catpeople)
        n_jobs=4
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
        elif name.startswith(DSCTOK):
            return doc_to_dsctok(cfg, catpeople)
            # --> entity_list_to_dsctok_csr_mat
            #     --> get_dsctok_from_catpeople_entity
            #         --> catpeople_sentence_iterator
            #         --> yield_dsctok
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
    args=arg_parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    if args.out_fn is None:
        if args.print_to_conll:
            args.out_fn = PFX+'/catpeople.conll.gz'
        else:
            args.out_fn = '%s/catpeople_pp_%d'%(PFX, args.config)
    main()
