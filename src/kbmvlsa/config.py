#!/usr/bin/env python
'''
| Filename    : config.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Dec  1 20:49:44 2016 (-0500)
| Last-Updated: Fri Dec  9 04:17:09 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 13
'''
import os
from os import path
RES_BASE = os.environ.get('KBMVLSA_RES_BASE', os.environ.get('HOME'))

DBPEDIA_TEST_DATA_DIR = path.join(
    RES_BASE, 'data/dbpedia-entity-search-test-collection')
QUERY_FN = path.join(DBPEDIA_TEST_DATA_DIR, 'queries.txt')
QRELS_FN = path.join(DBPEDIA_TEST_DATA_DIR, 'qrels.txt')

TREC_WEB_DATA_DIR = path.join(RES_BASE, 'data/chen-xiong-EntityRankData')
TREC_WEB_DBPEDIA_ZIP = path.join(TREC_WEB_DATA_DIR, 'dbpedia.trecweb.zip')
TREC_WEB_DBPEDIA_PKL = path.join(TREC_WEB_DATA_DIR, 'dbpedia.trecweb.pkl')
TREC_WEB_CATEGORIES = ['names', 'category', 'attributes', 'SimEn', 'RelEn']
RANK_SVM_INEX_LD = path.join(TREC_WEB_DATA_DIR, 'RankSVM_INEX-LD.run')

MVLSA_EMB_PKL_FN = path.join(
    RES_BASE, 'data/embedding/mvlsa/combined_embedding_0.emb.pkl')
DBPEDIA_PFXLEN = len('http://dbpedia.org/resource/')
