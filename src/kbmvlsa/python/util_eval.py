#!/usr/bin/env python
'''
| Filename    : util_eval.py
| Description : Utility functions for populating data.
| Author      : Pushpendre Rastogi
| Created     : Sat Dec  3 09:22:33 2016 (-0500)
| Last-Updated: Sat Dec  3 10:47:39 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
import config
from collections import OrderedDict, defaultdict

def get_qid_2_query_dict():
    ''' Return a dictionary that contains:
        {'INEX_LD-2009022': 'Szechwan dish food cuisine', ...}
    '''
    qid_2_query = {}
    with open(config.QUERY_FN) as file_handle:
        for (qid, query_string) in (row.strip().split('\t') for row in file_handle):
            qid_2_query[qid] = query_string.split()
    return qid_2_query


def get_qid_2_fsdm_top_100():
    ''' Return a dictionary that contains the top 100 answers that FSDM retrieves
        {'INEX_LD-2009022': ['http://dbpedia.org/resource/National_dish', ...]}
    '''
    qid_2_fsdm_top_100 = OrderedDict()
    with open(config.RANK_SVM_INEX_LD) as file_handle:
        for (qid, _, answer, _serial_no, _score, __) in (
                row.strip().split() for row in file_handle):
            try:
                qid_2_fsdm_top_100[qid].append(answer)
            except KeyError:
                qid_2_fsdm_top_100[qid] = [answer]
                pass
            pass
    return qid_2_fsdm_top_100

def get_qid_2_true_answer():
    qid_2_true_answer = defaultdict(list)
    with open(config.QRELS_FN) as file_handle:
        for (qid, _, answer, __) in (row.strip().split() for row in file_handle):
            qid_2_true_answer[qid].append(answer)
    qid_2_true_answer.default_factory = None
    return qid_2_true_answer
