#!/usr/bin/env python
# https://github.com/ContinuumIO/anaconda-issues/issues/152
# rpy2 import error due to libreadline undefined symbol
# Import rpy2 without importing readline causes an error.
# The dynamic file is not loaded in memory. The quickfix is to
# just import the readline library before trying to import robjects.
#  File "/home/hltcoe/prastogi/.local/lib/python2.7/site-packages/rpy2/rinterface/__init__.py", line 99, in <module>
#  from rpy2.rinterface._rinterface import *
#  ImportError: /opt/anaconda/lib/libreadline.so.6: undefined symbol: PC                                               
import readline
from rpy2 import robjects
import rpy2.robjects
import sklearn
from sklearn import linear_model
import numpy as np

def read_query_file(query_fn, name_to_idx_map):
    query_file_data = [e.strip() for e in open(query_fn)]
    query_data = []
    for (positive, negative) in zip(query_file_data[::2], query_file_data[1::2]):
        pos_category, pos_type, pos_example = positive.strip().split('\t')
        neg_category, neg_type, neg_example = negative.strip().split('\t')
        assert pos_category == neg_category
        assert pos_type == 'positive'
        assert neg_type == 'negative'
        knownRed_name = pos_example[1:-1].split(', ')
        knownNotRed_name = neg_example[1:-1].split(', ')
        knownRed_idx = [name_to_idx_map[e] for e in knownRed_name if e in name_to_idx_map]
        knownNotRed_idx = [name_to_idx_map[e] for e in knownNotRed_name if e in name_to_idx_map]
        query_data.append((pos_category, knownRed_idx, knownNotRed_idx))
    return query_data    

def write_to_file(f, category, values, vertex_names):
    f.write(category)
    f.write(' ')
    f.write(' '.join('%s=%.3f'%(nm, v) for (nm, v) in zip(vertex_names, values)))
    f.write('\n')
    f.flush()

def rpy2_matrix_to_numpy_matrix(m):
    arr = np.zeros((m.nrow, m.ncol))
    for row_idx in xrange(m.nrow):
        if row_idx % 5000 == 0:
            print (row_idx * 100) / m.nrow
        row = m.rx(1 + row_idx, True)
        for col_idx in xrange(m.ncol):
            arr[row_idx, col_idx] = row[col_idx]
    return arr

def get_features_and_name_from_r_file(vertex_feature_fn, vertex_name_fn):
    rpy2.robjects.r['load'](vertex_feature_fn)
    rpy2.robjects.r['load'](vertex_name_fn)
    vertex_features = rpy2_matrix_to_numpy_matrix(rpy2.robjects.r['vertex.features'])
    vertex_names = rpy2.robjects.r['vertex.names']
    return vertex_features, vertex_names

def main():
    vertex_features, vertex_names = get_features_and_name_from_r_file(
        args.vertex_feature_fn, args.vertex_name_fn)
    n_features = len(vertex_features[0])
    name_to_idx_map = dict((b, a) for (a,b) in enumerate(vertex_names))
    query_data = read_query_file(args.query_fn, name_to_idx_map)
    outputs = []
    f1 = open(args.output_fn_prefix + 'signed_distance', 'wb')
    f2 = open(args.output_fn_prefix + 'probability', 'wb')
    training_acc = {}
    for (category, pos, neg) in query_data:
        n_samples = len(pos)
        with rasengan.tictoc("Fitting And Scoring Model"):
            model = sklearn.linear_model.LogisticRegression(
                penalty='l2', dual=(n_features > n_samples), 
                solver='liblinear', verbose=1, n_jobs=4)
            X = np.concatenate(
                (vertex_features[pos], vertex_features[neg]), axis=0)
            Y = np.concatenate(
                (np.ones((len(pos),)), np.zeros((len(neg),))), axis=0)
            model = model.fit(X, Y)
            training_acc[category] = model.score(X, Y)
            print "Category", category, "Training Acc", training_acc[category]
            pass
        decisions = model.decision_function(vertex_features)
        probs = [e[0] for e in model.predict_proba(vertex_features)]
        write_to_file(f1, category, decisions, vertex_names)
        write_to_file(f2, category, probs, vertex_names)
        pass
    import cPickle as pickle
    pickle.dump(training_acc, open(args.output_fn_prefix + 'training_acc.pickle', 'wb'), protocol=-1)
    return


if __name__ == '__main__':
    _fn = "/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_maxd~100_ProjectToSphere~FALSE_Laplacian~FALSE"
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=1234, type=int)
    arg_parser.add_argument('--vertex_feature_fn', default=_fn, type=str)
    arg_parser.add_argument('--vertex_name_fn', default="/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.vertexnames", type=str)
    arg_parser.add_argument(
        '--query_fn', default="/home/hltcoe/ngao/miniScale-2016/Kelvin/VNSeeds", type=str)
    arg_parser.add_argument('--output_fn_prefix', default=_fn + '_logistic_', type=str)
    args=arg_parser.parse_args()
    import random
    random.seed(args.seed)
    np.random.seed(args.seed)

    import rasengan
    args.output_fn_prefix = args.output_fn_prefix.replace('logistic_probability', 'logistic_')
    print args
    with rasengan.debug_support():
        main()
