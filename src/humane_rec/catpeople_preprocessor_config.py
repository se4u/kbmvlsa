#!/usr/bin/env python
from rasengan import NamespaceLite
from functools import partial
import os
from catpeople_maligner_config_helper import Sequential_Policy, Fixed_Iter_Convergence
PROJECT_PATH = ['/export/b15/prastog3/',
                '~/data/embedding/',
                'data/']
UNIGRAM   = 'UNIGRAM'
UNIVEC    = 'UNIVEC'
BIGRAM    = 'BIGRAM'
BIVEC     = 'BIVEC'
DSCTOK    = 'DSCTOK'
DSCSUF    = 'DSCSUF'
DSCTOKVEC = 'DSCTOKVEC'

def config_maker(name, **kwargs):
    defaults = dict(only_entity_bearer=True, binarize_counts=True)
    for (k,v) in defaults.iteritems():
        if k not in kwargs:
            kwargs[k] = v
    return NamespaceLite(name, **kwargs)

DATACONFIG = NamespaceLite('Data',
                       fold_fn='cat-people-dev.fold.pkl',
                       cat2url_fn='cat-people-dev',
                       cp_fn='catpeople_clean_segmented_context.shelf')

NBDISCRT = 'NBDISCRT'
NBKERNEL = 'NBKERNEL'
KERMACH  = 'KERMACH'
MALIGNER = 'MALIGNER'
def expconfig_maker(name, **kwargs):
    defaults = dict(rm_fn_word=True, weight_method='log(1+tc)', top_token_pct=50, learn2rank=False, folds=(0,), verbose = True,)
    if name == NBKERNEL:
        defaults.update(dict(kernel='cosine'))
    if name == MALIGNER:
        defaults.update(dict(
            kernel='vanilla',
            malign_kernel='cosine',
            aggfn='avg',
            skim_pct=80,
            malign_method='fast_align',
            node_pick_policy=Sequential_Policy(),
            has_converged=Fixed_Iter_Convergence(50),
            respect_initial_assignment_for_initializing_beliefs=False,
            introduce_NULL_embedding = True,
            NULL_KEY = '--NULL--',
            scale_to_unit = True,
            mode_count=5,))
    for (k,v) in defaults.iteritems():
        if k not in kwargs:
            kwargs[k] = v
    return NamespaceLite(name, **kwargs)

CONFIG = {
    0: config_maker(UNIGRAM   , ),
    1: config_maker(UNIVEC    , vecfn='combined_embedding_0.emb.pkl'),
    2: config_maker(BIGRAM    , ),
    3: config_maker(BIVEC     , vecfn='combined_embedding_0.emb.pkl', aggfn='avg'),
    4: config_maker(DSCTOK    , parsefn='catpeople.parse.pkl'),
    5: config_maker(DSCSUF    , parsefn='catpeople.parse.pkl'),
    6: config_maker(DSCTOKVEC , vecfn='combined_embedding_0.emb.pkl', parsefn=''),
    # Switch entity bearer to False
    7: config_maker(UNIGRAM   , only_entity_bearer=False, ),
    8: config_maker(UNIVEC    , only_entity_bearer=False, vecfn='combined_embedding_0.emb.pkl'),
    9: config_maker(BIGRAM    , only_entity_bearer=False, ),
    10: config_maker(BIVEC    , only_entity_bearer=False, vecfn='combined_embedding_0.emb.pkl', aggfn='avg'),
    11: config_maker(DSCTOK   , only_entity_bearer=False, parsefn='catpeople.parse.pkl'),
    12: config_maker(DSCSUF   , only_entity_bearer=False, parsefn='catpeople.parse.pkl'),
    13: config_maker(DSCTOKVEC, only_entity_bearer=False, vecfn='combined_embedding_0.emb.pkl', parsefn='catpeople.parse.pkl'),
    ## Dont Binarize Counts
    14: config_maker(UNIGRAM   , binarize_counts=False, ),
    15: config_maker(UNIVEC    , binarize_counts=False, vecfn='combined_embedding_0.emb.pkl'),
    16: config_maker(BIGRAM    , binarize_counts=False, ),
    17: config_maker(BIVEC     , binarize_counts=False, vecfn='combined_embedding_0.emb.pkl', aggfn='avg'),
    18: config_maker(DSCTOK    , binarize_counts=False, parsefn='catpeople.parse.pkl'),
    19: config_maker(DSCSUF    , binarize_counts=False, parsefn='catpeople.parse.pkl'),
    20: config_maker(DSCTOKVEC , binarize_counts=False, vecfn='combined_embedding_0.emb.pkl', parsefn=''),
    # Switch entity bearer to False
    21: config_maker(UNIGRAM   , binarize_counts=False, only_entity_bearer=False, ),
    22: config_maker(UNIVEC    , binarize_counts=False, only_entity_bearer=False, vecfn='combined_embedding_0.emb.pkl'),
    23: config_maker(BIGRAM    , binarize_counts=False, only_entity_bearer=False, ),
    24: config_maker(BIVEC    , binarize_counts=False, only_entity_bearer=False, vecfn='combined_embedding_0.emb.pkl', aggfn='avg'),
    25: config_maker(DSCTOK   , binarize_counts=False, only_entity_bearer=False, parsefn='catpeople.parse.pkl'),
    26: config_maker(DSCSUF   , binarize_counts=False, only_entity_bearer=False, parsefn='catpeople.parse.pkl'),
    27: config_maker(DSCTOKVEC, binarize_counts=False, only_entity_bearer=False, vecfn='combined_embedding_0.emb.pkl', parsefn='catpeople.parse.pkl'),
}

EXPCONFIG = {
    # NBDISCRT < 100
    0: expconfig_maker(NBDISCRT, ),
    1: expconfig_maker(NBDISCRT, rm_fn_word=False),
    2: expconfig_maker(NBDISCRT, top_token_pct=0),
    3: expconfig_maker(NBDISCRT, weight_method='log(1+tc)/df'),
    # 100 < NBKERNEL < 200
    100: expconfig_maker(NBKERNEL, ),
    101: expconfig_maker(NBKERNEL, weight_method='log(1+tc)/df'),
    # 200 < KERMACH < 300
    200: expconfig_maker(KERMACH, kernel='rada'),
    201: expconfig_maker(KERMACH, kernel='se'),
    # 300 < MALIGNER
    300: expconfig_maker(MALIGNER, ),
    301: expconfig_maker(MALIGNER, top_token_pct=0),
    302: expconfig_maker(MALIGNER, top_token_pct=0, skim_pct=0),
}


if __name__ == '__main__':
    for i in range(len(CONFIG)):
        print '%-2d'%i, '%-120s'%str(CONFIG[i]), i
    print
    for i in range(len(EXPCONFIG)):
        print '%-2d'%i, '%-120s'%str(EXPCONFIG[i]), i
