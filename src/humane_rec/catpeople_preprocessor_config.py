#!/usr/bin/env python
from rasengan import NamespaceLite
from functools import partial
import os
PROJECT_PATH = [('/export/b15/prastog3' if os.uname()[1] == 'b15' else 'data'),
                '~/data/embedding/']
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
}


DATACONFIG = NamespaceLite('Data',
                       fold_fn='cat-people-dev.fold.pkl',
                       cat2url_fn='cat-people-dev',
                       cp_fn='catpeople_clean_segmented_context.shelf')

NB       = 'NB'
NBKERNEL = 'NBKERNEL'
KERMACH  = 'KERMACH'
MALIGNER = 'MALIGNER'
def expconfig_maker(name, **kwargs):
    defaults = dict(rm_fn_word=True, weight_method='log(1+tc)', top_token_pct=70, kernel='cosine')
    for (k,v) in defaults.iteritems():
        if k not in kwargs:
            kwargs[k] = v
    return NamespaceLite(name, **kwargs)

EXPCONFIG = {
    0: expconfig_maker(NB, ),
    1: expconfig_maker(NB, rm_fn_word=False),
    2: expconfig_maker(NB, top_token_pct=0),
    3: expconfig_maker(NBKERNEL, ),
    4: expconfig_maker(NBKERNEL, kernel='l2'),
    5: expconfig_maker(KERMACH, kernel='rada'),
    6: expconfig_maker(KERMACH, kernel='se'),
    7: expconfig_maker(MALIGNER, ),
}



if __name__ == '__main__':
    for i in range(len(CONFIG)):
        print '%-2d'%i, '%-120s'%str(CONFIG[i]), i
    print
    for i in range(len(EXPCONFIG)):
        print '%-2d'%i, '%-120s'%str(EXPCONFIG[i]), i
