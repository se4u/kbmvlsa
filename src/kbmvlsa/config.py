#!/usr/bin/env python
'''
| Filename    : config.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Dec  1 20:49:44 2016 (-0500)
| Last-Updated: Sat Dec 24 05:55:02 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 30
'''
import os
from os import path
RES_BASE = os.environ.get('KBMVLSA_RES_BASE', os.environ.get('HOME'))

DBPEDIA_TEST_DATA_DIR = path.join(
    RES_BASE, 'data/dbpedia-entity-search-test-collection')
QUERY_FN = path.join(DBPEDIA_TEST_DATA_DIR, 'queries.txt')
QRELS_FN = path.join(DBPEDIA_TEST_DATA_DIR, 'qrels.txt')

TREC_WEB_DATA_DIR = path.join(RES_BASE, 'data/chen-xiong-EntityRankData')
# Some quick facts about dbpedia.trecweb.zip
# 1. zipout ~/data/chen-xiong-EntityRankData/dbpedia.trecweb.zip | fgrep -c '</DOC>'
#    takes almost 8 minutes and shows that there are 9.5M entries.
#    Each record contributes 22 lines, which means that there are 209M lines
#    in the buffer. (actually 210M  %)
# 2. Reading these 9.5 million entries in python takes a long time.
#    It takes 23 min to even read 63M lines.
#    Without even doing any updates, this means that even without counting
#    anything, just reading the files in python will take 76.3 minutes.
# 3. When I add processing then it takes 8 min to read 4.7M lines, which means
#    processing the file will take 526 minutes = 9hr.
#    And after 9 hour, I will start the process of pickling and writing to file.
#    And this will take a lot of memory as well.
TREC_WEB_DBPEDIA = path.join(TREC_WEB_DATA_DIR, 'dbpedia.trecweb', 'dbpedia.trecweb')
TREC_WEB_DBPEDIA_SMALL = path.join(TREC_WEB_DATA_DIR, 'dbpedia.trecweb', 'dbpedia.trecweb.small')
TREC_WEB_DBPEDIA_ZIP = path.join(TREC_WEB_DATA_DIR, 'dbpedia.trecweb.zip')
TREC_WEB_DBPEDIA_GZ = path.join(TREC_WEB_DATA_DIR, 'dbpedia.trecweb.gz')
TREC_WEB_TOKEN_PKL = path.join(RES_BASE,
                               "export/kbmvlsa/dbpedia.trecweb.field_tokens.pkl")
TREC_WEB_HIT_LIST_PKL = path.join(RES_BASE,
                                  "export/kbmvlsa/dbpedia.trecweb.hit_list.pkl")
TREC_WEB_CATEGORIES = ['names', 'category', 'attributes', 'SimEn', 'RelEn']
TREC_WEB_CATEGORIES_STR = ' '.join(TREC_WEB_CATEGORIES)
RANK_SVM_INEX_LD = path.join(TREC_WEB_DATA_DIR, 'RankSVM_INEX-LD.run')
MVLSA_EMB_PKL_FN = path.join(
    RES_BASE, 'data/embedding/mvlsa/combined_embedding_0.emb.pkl')
DBPEDIA_PFXLEN = len('http://dbpedia.org/resource/')
