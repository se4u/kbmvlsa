#!/usr/bin/env python
'''
| Filename    : config.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Dec  1 20:49:44 2016 (-0500)
| Last-Updated: Sat Dec  3 10:59:00 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 5
'''
import os
from os import path
RES_BASE = os.environ.get('KBMVLSA_RES_BASE', os.environ.get('HOME'))
QUERY_FN = path.join(RES_BASE, 'data/dbpedia-entity-search-test-collection/queries.txt')
QRELS_FN = path.join(RES_BASE, 'data/dbpedia-entity-search-test-collection/qrels.txt')
RANK_SVM_INEX_LD = path.join(RES_BASE, 'data/chen-xiong-EntityRankData/RankSVM_INEX-LD.run')
MVLSA_EMB_PKL_FN = path.join(RES_BASE, 'data/embedding/mvlsa/combined_embedding_0.emb.pkl')
DBPEDIA_PFXLEN = len('http://dbpedia.org/resource/')
import itertools
itertools.chain
import numpy
numpy.random.randint()