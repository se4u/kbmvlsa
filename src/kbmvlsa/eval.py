#!/usr/bin/env python
'''
| Filename    : eval.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Dec  1 20:46:46 2016 (-0500)
| Last-Updated: Thu Dec  8 17:37:35 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 35
All learning to rank methods are quite simple, the goal is to learn a model
that can optimize a metric like MAP, or ROC given a few examples. In my case
I can start with a list of things that the true FSDM code returns, thanks to
chenyan's results files, and then rerank those things.
'''
import config
import numpy
import cPickle as pkl
import os
from class_fold_iterator import FoldIterator
from util_eval import get_qid_2_query_dict, get_qid_2_fsdm_top_100, \
    get_qid_2_true_answer


def get_token_vec(token, mvlsa_word_emb_data):
    if token in mvlsa_word_emb_data:
        return mvlsa_word_emb_data[token]
    return None


def get_query_vec(query_token_list, mvlsa_word_emb_data):
    # TODO: The real program should do these things automatically. For now
    # I have manually made these changes to the query files.
    # 1. Taking care of apostrophes, remove traling aprostrophes
    # 2. Splitting hyphens
    # 3. Removing other punctuation
    query_vec = [get_token_vec(token, mvlsa_word_emb_data) for token in query_token_list]
    filtered_vec = [e for e in query_vec if e is not None]
    if len(filtered_vec) == 0:
        return numpy.zeros((300,))
    return numpy.mean(filtered_vec, axis=0)


def feat_string(query_vec, answer_vec):
    vec = numpy.outer(query_vec[:25], answer_vec[:25]).ravel() * 1000
    assert not numpy.isnan(vec).any()
    return ''.join('%d:%.3e '%(i+1,e) for i,e in enumerate(vec))


def train_model(training_query_ids, true_answer_entities, entities_retrieved_by_fsdm, entity_vec_dict, mvlsa_data, query_id_to_question_tokens,
                train_data_fn = '/tmp/train_data_fn',
                model_fn = '/tmp/model_fn'):
    '''
    --- INPUT ---
    training_query_ids          : [INEX_LD-2009022', ...]
    true_answer_entities        : {'INEX_LD-2009022': ['http://dbpedia.org/resource/Indian_Chinese_cuisine', ...], ...}
    entities_retrieved_by_fsdm  : {'INEX_LD-2009022': ['http://dbpedia.org/resource/National_dish', ...], ...}
    entity_vec_dict             : {'http://dbpedia.org/resource/National_dish': [300d 'float64' array]], ...}
    mvlsa_data                  : {'star': [300d 'float64' array]}
    query_id_to_question_tokens : {'INEX_LD-2009022': ['Szechwan', 'dish', 'food', 'cuisine']}
    '''
    with open(train_data_fn, 'wb') as train_data_f:
        for numeric_qid, qid in enumerate(training_query_ids):
            numeric_qid += 1
            query_vec = get_query_vec(query_id_to_question_tokens[qid], mvlsa_data)
            true_answer_set = set(true_answer_entities[qid])
            for answer in true_answer_set:
                train_data_f.write('1 qid:%d %s\n'%(
                    numeric_qid,
                    feat_string(query_vec,
                                get_query_vec(answer[config.DBPEDIA_PFXLEN:].strip().split('_'),
                                              mvlsa_data))))

            for answer in entities_retrieved_by_fsdm[qid]:
                if answer not in true_answer_set:
                    train_data_f.write('0 qid:%d %s\n'%(
                        numeric_qid,
                        feat_string(query_vec,
                                    get_query_vec(answer[config.DBPEDIA_PFXLEN:].split('_'),
                                                  mvlsa_data))))

    os.system('~/data/svm_rank/svm_rank_learn -c 10 %s %s'%(train_data_fn, model_fn))
    return model_fn


def test_model(testing_query_ids, entities_retrieved_by_fsdm, entity_vec_dict, mvlsa_data, query_id_to_question_tokens, true_answer_entities,
               model_fn = '/tmp/model_fn', test_data_fn='/tmp/test_data_fn', prediction_fn='/tmp/prediction_fn'):
    '''
    --- INPUT ---
    testing_query_ids           :
    entities_retrieved_by_fsdm  :
    entity_vec_dict             :
    mvlsa_data                  :
    query_id_to_question_tokens :
    --- OUTPUT ---
    '''
    with open(test_data_fn, 'wb') as test_data_f:
        for numeric_qid, qid in enumerate(testing_query_ids):
            numeric_qid += 1
            query_vec = get_query_vec(query_id_to_question_tokens[qid], mvlsa_data)
            true_answer_set = set(true_answer_entities[qid])
            for answer in entities_retrieved_by_fsdm[qid]:
                test_data_f.write('%d qid:%d %s\n'%(
                    int(answer in true_answer_set),
                    numeric_qid,
                    feat_string(query_vec,
                                get_query_vec(answer[config.DBPEDIA_PFXLEN:].split('_'),
                                              mvlsa_data))))
    os.system('~/data/svm_rank/svm_rank_classify %s %s %s'%(test_data_fn, model_fn, prediction_fn))
    return prediction_fn


def evaluate(test_data_fn='/tmp/test_data_fn', prediction_fn='/tmp/prediction_fn'):
    # for e in `seq 100 100 1000` ; do paste <( awk '{print substr($2, 5), $1}' test_data_fn ) prediction_fn | hn $e | tn 100 | sort -s -k 3,3 -n -r | hn 20 | grep -v '0.00000' | sumColumns '$2' ; done | avgColumns
    print 'MAP', 'P@10', 'P@20'
    return

def main():
    qid_2_query = get_qid_2_query_dict()
    qid_2_fsdm_top_100 = get_qid_2_fsdm_top_100()
    qid_2_true_answer = get_qid_2_true_answer()
    mvlsa_data = pkl.load(open(config.MVLSA_EMB_PKL_FN, mode="rb"))
    entity_vec_dict = pkl.load(open("kbmvlsa_embedding.pkl", mode="rb"))
    for (train_ent, test_ent) in FoldIterator(n=5, list_to_fold=qid_2_fsdm_top_100):
        print(len(train_ent))
        print(len(test_ent))
        model_fn = train_model(train_ent, qid_2_true_answer, qid_2_fsdm_top_100, entity_vec_dict, mvlsa_data, qid_2_query)
        prediction_fn = test_model(test_ent, qid_2_fsdm_top_100, entity_vec_dict, mvlsa_data, qid_2_query, qid_2_true_answer,
                                   model_fn=model_fn)
        print(evaluate(test_ent, qid_2_true_answer, prediction_fn))
    return

if __name__ == '__main__':
    main()
