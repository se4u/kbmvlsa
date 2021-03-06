#!/usr/bin/env python
'''
| Filename    : catpeople_experiment.py
| Description : The Experiment Loop
| Author      : Pushpendre Rastogi
| Created     : Fri Sep 23 13:05:58 2016 (-0400)
| Last-Updated: Sat Oct  1 20:22:31 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 228
'''
import argparse
import random
import numpy as np
from catpeople_preprocessor_config import UNIGRAM, UNIVEC, BIGRAM, BIVEC, \
    DSCTOK, DSCSUF, DSCTOKVEC, CONFIG, DATACONFIG, EXPCONFIG, NBDISCRT, NBKERNEL, \
    KERMACH, MALIGNER, UNISUF
import util_catpeople as uc
from util_catpeople import set_column_of_sparse_matrix_to_zero
from shelve import DbfilenameShelf
from performance_aggregator import Aggregator
import cPickle as pkl
import scipy
import scipy.sparse
from scipy import io
from pandas import DataFrame
import maligner
import rasengan
import numpy.matrixlib.defmatrix
import itertools
import collections

def prefix(cfg, lst):
    return (any(cfg._name.startswith(e + '.') for e in lst)
            if isinstance(lst, list)
            else cfg._name.startswith(lst + '.'))

def scale_to_unit(v):
    assert v.ndim == 1
    n = np.linalg.norm(v)
    return (v if n == 0 else v / n)


def sparse_multiply(a, b):
    assert a.shape == b.shape
    if isinstance(a, numpy.matrixlib.defmatrix.matrix):
        if a.shape[0] == 1:
            a1 = a.shape[1]
            return b * scipy.sparse.spdiags(a, 0, a1, a1)
        elif a.shape[1] == 1:
            a0 = a.shape[0]
            return scipy.sparse.spdiags(a, 0, a0, a0) * b
        else:
            raise ValueError((a,b))
    elif (scipy.sparse.isspmatrix_csr(a) or scipy.sparse.isspmatrix_csc(a)):
        return a.multiply(b)

def sparse_log1p(a):
    assert isinstance(a, numpy.matrixlib.defmatrix.matrix)
    return


class ExperimentRunner(object):
    def is_malignull(self):
        return self.exp_prefix_is(MALIGNER) and self.expcfg.introduce_NULL_embedding

    def __init__(self, datacfg, ppcfg, expcfg):
        # Init Part 0
        self.datacfg = datacfg
        self.ppcfg = ppcfg
        self.expcfg = expcfg

        with rasengan.tictoc('Init Part 1 : The Datacfg'):
            self.cp = DbfilenameShelf(
                r'%s/%s'%(uc.get_pfx(),self.datacfg.cp_fn),
                protocol=-1,
                flag='r')
            self.url_list = self.cp['__URL_LIST__']
            self.TM = self.cp['__TOKEN_MAPPER__']
            # self.TM.final must be patched to work with older
            # versions of TokenMapper that are in the pickle.
            if not hasattr(self.TM, 'final'):
                self.TM.final = False
            if self.is_malignull():
                self.TM([self.expcfg.NULL_KEY])
            self.bos_idx = self.TM.finalize()
            self.pa = Aggregator(
                datacfg=datacfg,
                ppcfg=ppcfg,
                expcfg=expcfg,
                url_list=self.url_list,
                TM=self.TM)
            self.cat_folds = pkl.load(uc.proj_open(self.datacfg.fold_fn))
            self.cat2url = uc.load_cat2url(uc.proj_open(self.datacfg.cat2url_fn))
            self.url_to_idx = dict((b,a) for a,b in enumerate(self.url_list))
            self.scratch = {}
            pass

        with rasengan.tictoc('Init Part 2 : The PP CFG'):
            print 'Reading', 'catpeople_pp_%d'%args.ppcfg
            self.smat = io.mmread(uc.proj_open('catpeople_pp_%d'%args.ppcfg))
            assert scipy.sparse.isspmatrix_coo(self.smat)
            if self.pp_prefix_is([UNIVEC, BIVEC, MALIGNER, DSCTOKVEC]):
                self.vectors = np.load(uc.proj_open('catpeople_pp_%d.vec'%args.ppcfg))
            pass

        if self.is_malignull():
            self.NULL_VEC = np.zeros((1,self.vectors.shape[1]))
        if self.exp_prefix_is([NBKERNEL, KERMACH, MALIGNER]):
            assert self.pp_prefix_is([UNIVEC, BIVEC, DSCTOKVEC])
        if self.expcfg.rm_fn_word:
            # Internally Manipulates smat
            self.remove_fn_word()
        if self.expcfg.weight_method.endswith('/df'):
            self.populate_idf()
        return

    def populate_idf(self):
        entities = float(self.smat.shape[0])
        self.idf = np.log(entities / self.smat.sum(axis=0))
        assert self.idf.shape[1] == self.smat.shape[1]
        return

    def exp_prefix_is(self, lst_or_str):
        return prefix(self.expcfg, lst_or_str)

    def pp_prefix_is(self, lst_or_str):
        return prefix(self.ppcfg, lst_or_str)

    def remove_fn_word(self):
        ''' Manipulate `self.smat` and remove indices corresponding to fn words.
        '''
        from rasengan.function_words import get_function_words
        self.fnwords = []
        for e in itertools.chain(get_function_words(), ['ago', 'well', 'years']):
            try:
                self.fnwords.append(self.TM(e.lower()))
            except KeyError:
                continue
        column_idi =  set(self.fnwords)
        self.pa['fnwords'] = column_idi
        if self.pp_prefix_is([UNIVEC, UNIGRAM, DSCTOK, DSCTOKVEC]):
            pass
        elif self.pp_prefix_is([BIVEC, BIGRAM]):
            column_idi = set(list(column_idi)
                             + self.get_col_index_of_function_bigrams())
        elif self.pp_prefix_is([UNISUF, DSCSUF]):
            column_idi = set(list(column_idi)
                             + self.get_col_index_of_function_govgrams())
        else:
            raise NotImplementedError(self.ppcfg._name)
        self.smat = set_column_of_sparse_matrix_to_zero(self.smat, column_idi)
        return

    def get_col_index_of_function_govgrams(self):
        ''' Returns indices of (governor label, unigrams) that
        indicate function words.
        '''
        fnwords = set(self.fnwords)
        base = len(self.TM)
        nonempty_columns = set(self.smat.col)
        l = []
        for ci in nonempty_columns:
            cur = ci % base
            if cur in fnwords:
                l.append(ci)
        return l

    def get_col_index_of_function_bigrams(self):
        # uc.patch_scipy(scipy)
        fnwords = set(self.fnwords)
        base = len(self.TM)
        nonempty_columns = set(self.smat.col)
        l = []
        for ci in nonempty_columns:
            cur = ci % base
            if cur in fnwords:
                l.append(ci)
                continue
            prv = (ci - cur) / base - 1
            if prv in fnwords:
                l.append(ci)
        return l

    def call_impl(self, cat, train_idx, test_idx):
        with rasengan.tictoc('Fitting'):            # 2.1s
            self.fit(self.smat[train_idx], train_idx=train_idx)
        self.smat = self.smat.tocsr()
        with rasengan.tictoc('Prediction'):         # 20s
            scores = self.score(self.smat)
        self.pa(cat, scores, train_idx, test_idx, scratch=self.scratch)
        self.scratch = {}

    def __call__(self):
        print 'Total=', len(list(self.fold_iterator()))
        for fold_idx, (cat, (train_idx, test_idx)) in enumerate(self.fold_iterator()):
            if self.expcfg.verbose:
                print 'Working on %-4d'%fold_idx, cat,
            self.call_impl(cat, train_idx, test_idx)
        return

    @staticmethod
    def get_top_occurring_col(mat, pct, reverse=False):
        ''' Return column indices that are nonzero strictly more
        than (pct)/100*rows number of times.
        --- INPUT ---
        mat     :
        pct     : The threshold in percentage.
        reverse : When reverse is true then we return column idi that
                  are nonzero less than equal to threshold number of
                  times. (default False)
        --- OUTPUT ---
        A list of integer column indices.
        '''
        threshold = (pct * mat.shape[0])/100.0
        if scipy.sparse.isspmatrix_coo(mat):
            cntr = collections.Counter(mat.col)
            if reverse:
                return [i for i,v in cntr.iteritems() if v <= threshold]
            else:
                return [i for i,v in cntr.iteritems() if v > threshold]
        else:
            colsum = mat.sum(axis=0)
            if reverse:
                return (colsum <= threshold).nonzero()[1]
            else:
                return (colsum > threshold).nonzero()[1]

    def keep_only_top_occurring_tokens(self, mat):
        bottom_col = self.get_top_occurring_col(
            mat, self.expcfg.top_token_pct, reverse=True)
        return set_column_of_sparse_matrix_to_zero(mat, list(bottom_col))


    def create_token_weights(self, mat):
        wm = self.expcfg.weight_method
        if wm == 'log(1+tc)':
            w = np.log1p(mat.sum(axis=0))
        elif wm == 'log(1+tc)/df':
            w = sparse_multiply(np.log1p(mat.sum(axis=0)),  self.idf)
        self.token_weight = w

    def create_malign_problem(self, mat, undesirable_columns, train_idx):
        problem = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
        for row_idx, entity_idx in zip(range(mat.shape[0]), train_idx):
            # row = mat[row_idx]
            index = [i for i in mat.indices[mat.indptr[row_idx]:mat.indptr[row_idx+1]]
                     if  i not in undesirable_columns]
            if len(index) == 0:
                continue
            process = (scale_to_unit
                       if self.expcfg.scale_to_unit
                       else (lambda x: x))
            data = [process(self.vectors[i])[None,:] for i in index]
            if self.expcfg.introduce_NULL_embedding:
                index.append(self.TM(self.expcfg.NULL_KEY))
                data.append(self.NULL_VEC)
            problem[self.url_list[entity_idx]] = DataFrame(
                data=np.concatenate(data, axis=0),
                index=index) # [str(e) for e in index])
        return problem

    def extract_malign_topics(self, mat, train_idx):
        # First get the top columns.
        # These columns are topics of their own.
        top_col = list(self.get_top_occurring_col(mat, self.expcfg.skim_pct))
        # Now extract self.expcfg.mode_count modes from non-exact token matches.
        # Each mode is a collection of tokens and its now a topic.
        mat = mat.tocsr()
        topics = [[e] for e in top_col]
        undesirable_columns = top_col
        for _ in range(self.expcfg.mode_count):
            problem = self.create_malign_problem(mat, set(undesirable_columns), train_idx)
            if len(problem) == 0:
                break
            assignment = {}
            for entity in problem:
                assignment[entity] = 0
            topic = self.extract_mode(problem, assignment)
            topics.append(topic)
            tv = topic.values()
            if self.expcfg.verbose:
                print self.TM[tv]
            undesirable_columns.extend(topic.values())
        self.topics = topics
        return

    def extract_mode(self, problem, assignment):
        assert self.expcfg.malign_method == 'fast_align'
        assert self.expcfg.malign_kernel == 'cosine'
        return maligner.fast_relax(problem, assignment, self.expcfg)


    def fit(self, mat, train_idx):
        mat = self.keep_only_top_occurring_tokens(mat)
        if self.exp_prefix_is([NBDISCRT, NBKERNEL]):
            self.create_token_weights(mat)
        elif self.exp_prefix_is(MALIGNER):
            self.extract_malign_topics(mat, train_idx)
        elif self.exp_prefix_is(KERMACH):
            raise NotImplementedError()
        else:
            raise NotImplementedError()
        if self.expcfg.learn2rank:
            raise NotImplementedError()
        return

    def score(self, mat):
        if self.exp_prefix_is(NBDISCRT):
            return self.score_nb(mat)
        if self.exp_prefix_is(NBKERNEL):
            return self.score_nbkernel(mat)
        elif self.exp_prefix_is(MALIGNER):
            return self.score_malign(mat)
        elif self.exp_prefix_is(KERMACH):
            return self.score_kernelmachine(mat)

        raise NotImplementedError()

    def score_nb(self, mat):
        '''
        mat : Is a matrix of features that each document corresponds to.
        It may be real valued weights of unigrams or binary occurrences of
        bigrams.

        The output is a list of floats, one float for each row in the matrix.
        '''
        w = self.token_weight
        self.scratch['score_nb_features'] = (self.TM[w.nonzero()[1]], w[:,w.nonzero()[1]])
        if self.expcfg.verbose:
            print 'Rating NB using features', self.scratch['score_nb_features']
        return mat * w.T

    def score_nbkernel(self, mat):
        scorer = self.get_nbkernel_scorer()
        return [scorer(mat[i]) for i in xrange(mat.shape[0])]

    def score_malign(self, mat):
        scorer = self.get_malign_scorer()
        if self.expcfg.aggfn == 'nblike':
            vectors = scorer
            return mat * vectors
        else:
            return [scorer(mat[i]) for i in xrange(mat.shape[0])]

    def score_kernelmachine(self, mat):
        scorer = self.get_kernelmachine_scorer()
        return [scorer(mat[i]) for i in xrange(mat.shape[0])]

    def get_nbkernel_scorer(self):

        def scorer(row):
            return score

        return scorer

    def get_kernelmachine_scorer(self):

        def scorer(row):
            return score

        return scorer

    def get_malign_scorer(self):
        if self.expcfg.aggfn == 'avg':
            vectors = []
            if len(self.topics):
                for tpc in self.topics:
                    if isinstance(tpc, dict):
                        tpc = tpc.values()
                    elif isinstance(tpc, list):
                        pass
                    else:
                        raise NotImplementedError(tpc)
                    vectors.append(sum(self.vectors[i] for i in tpc) / len(tpc))
            else:
                vectors = 0
            vectors = np.array(vectors)
            assert vectors.shape[0] == len(self.topics)
        elif self.expcfg.aggfn == 'nblike':
            weight = {}
            for tpc_idx, tpc in enumerate(self.topics):
                tpc = set(tpc.values()
                          if isinstance(tpc, dict)
                          else tpc)
                for tok in tpc:
                    weight[tok] = (1.0 / (tpc_idx + 1)**2)
            vectors = rasengan.csr_mat_builder([weight], (1, len(self.TM)-1), dtype='float32', verbose=0).T
            if self.expcfg.verbose:
                tmp1, tmp2 = zip(*weight.items())
                print self.TM[list(tmp1)], tmp2
            return vectors
        else:
            raise ValueError(self.expcfg.aggfn)

        def scorer(row):
            score = 0.0
            columns = list(row.nonzero()[1])
            if self.expcfg.kernel == 'vanilla':
                # Score = average over score of each topic.
                # Score of each topic = best score of topic with any token.
                score = np.dot(vectors, self.vectors[columns].T).max(axis=1).mean()
            elif self.expcfg.kernel == 'buttercup':
                # Score = average over score of each token.
                # Score of each token = best score of token with any topic
                score = np.dot(vectors, self.vectors[columns].T).max(axis=0).mean()
                # ------------------------------ #
                # SLOW VERSION OF THE ABOVE CODE #
                # ------------------------------ #
                # for col in columns:
                #     vec = self.vectors[col]
                #     s = np.dot(vectors, vec).max()
                #     score += s
            elif self.expcfg.kernel == 'nblike':
                score = (row * vectors).data
            elif self.expcfg.kernel == 'l2':
                raise NotImplementedError(self.expcfg.kernel)
            else:
                raise NotImplementedError(self.expcfg.kernel)
            return score

        return scorer

    def fold_iterator(self):
        for cat, folds in self.cat_folds.iteritems():
            url_in_cat = self.cat2url[cat]
            mapper = lambda lst : [self.url_to_idx[url_in_cat[i]] for i in lst]
            for fold_idx, fold in enumerate(folds):
                if fold_idx in self.expcfg.folds:
                    yield cat, (mapper(fold[0]), mapper(fold[1]))

    def report(self):
        print self.pa

    def save_results(self, fn=None):
        if fn is None:
            fn = args.out_pkl_fn
        pkl.dump(self.pa, open(fn, 'wb'))



def populate_args():
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int)
    arg_parser.add_argument('--ppcfg', default=1, type=int)
    arg_parser.add_argument('--expcfg', default=0, type=int)
    arg_parser.add_argument('--out_pkl_fn', default=None, type=str)
    args=arg_parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    if args.out_pkl_fn is None:
        args.out_pkl_fn = (
            uc.get_pfx()
            + 'catpeople_experiment.ppcfg~%d.expcfg~%d.pkl'%(args.ppcfg, args.expcfg))
    return args

def main():
    global args
    args = populate_args()
    rnr = ExperimentRunner(
        datacfg=DATACONFIG,
        ppcfg=CONFIG[args.ppcfg],
        expcfg=EXPCONFIG[args.expcfg],)
    rnr()
    with rasengan.tictoc('Saving Results'):
        rnr.save_results(fn=args.out_pkl_fn)
    with rasengan.tictoc('Reporting'):
        rnr.report()

if __name__ == '__main__':
    with rasengan.debug_support():
        main()
#  Local Variables:
#  eval: (progn (anaconda-mode -1) (eldoc-mode -1) (company-mode -1) (linum-mode 1))
#  End:
