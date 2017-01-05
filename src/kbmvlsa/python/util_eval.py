#!/usr/bin/env python
'''
| Filename    : util_eval.py
| Description : Utility functions for populating data.
| Author      : Pushpendre Rastogi
| Created     : Sat Dec  3 09:22:33 2016 (-0500)
| Last-Updated: Wed Jan  4 23:16:15 2017 (-0500)
|           By: System User
|     Update #: 27
'''
import config
from collections import OrderedDict, defaultdict
import itertools

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


def get_all_relevant_entities():
    s = set()
    for e in itertools.chain(get_qid_2_fsdm_top_100().itervalues(),
                             get_qid_2_true_answer().itervalues()):
        s.update(e)
    return s


def create_embbedding_feature_dict(emb_feat_fn, out_fn):
    import cPickle, numpy
    arr = numpy.load(emb_feat_fn, mmap_mode='r', allow_pickle=False)
    docno2idx = cPickle.load(open(config.TREC_WEB_DOCNO2ID_PKL))
    emb = {}
    for ent in get_all_relevant_entities():

        try:
            idx = docno2idx[ent]
        except KeyError:
            e = ent.split('%23')
            if len(e) == 2:
                idx = docno2idx[e[0]]
            else:
                assert ent == 'http://dbpedia.org/resource/Template:Edward_D._Wood,_Jr.'
                idx = docno2idx['http://dbpedia.org/resource/Edward_D._Wood,_Jr.']
        emb[ent] = arr[idx][-300:]
    with open(out_fn, 'wb') as f:
        print 'Saving to ', out_fn
        cPickle.dump(emb, f)

if __name__ == '__main__':
    import config, os
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument(
        '--emb_feat_fn', type=str,
        default='Mvlsa@intermediate_dim~300@view_transform~TFIDF@mean_center~0')
    args=arg_parser.parse_args()
    emb_feat_fn = os.path.join(config.TREC_WEB_STORAGE, args.emb_feat_fn)
    out_fn = emb_feat_fn + '.small.pkl'
    create_embbedding_feature_dict(emb_feat_fn, out_fn)
