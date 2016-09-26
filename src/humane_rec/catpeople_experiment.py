#!/usr/bin/env python
'''
| Filename    : catpeople_experiment.py
| Description : The Experiment Loop
| Author      : Pushpendre Rastogi
| Created     : Fri Sep 23 13:05:58 2016 (-0400)
| Last-Updated: Mon Sep 26 14:29:42 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 148
'''
import argparse
import random
import numpy as np
from catpeople_preprocessor_config import UNIGRAM, UNIVEC, BIGRAM, BIVEC, \
    DSCTOK, DSCSUF, DSCTOKVEC, CONFIG, DATACONFIG, EXPCONFIG, NBDISCRT, NBKERNEL, \
    KERMACH, MALIGNER
import util_catpeople as uc
from shelve import DbfilenameShelf
from performance_aggregator import Aggregator
import cPickle as pkl
import scipy.sparse
from scipy import io
from pandas import DataFrame
import maligner
import rasengan
import numpy.matrixlib.defmatrix


def prefix(cfg, lst):
    return (any(cfg._name.startswith(e + '.') for e in lst)
            if isinstance(lst, list)
            else cfg._name.startswith(lst + '.'))

def scale_to_unit(v):
    assert v.ndim == 1
    n = np.linalg.norm(v)
    return (v if n == 0 else v / n)

def set_column_of_sparse_matrix_to_zero(smat, col_idi):
    if not isinstance(smat, scipy.sparse.csc_matrix):
        smat = smat.tocsc()
    for col_idx in col_idi:
        smat.data[smat.indptr[col_idx]:smat.indptr[col_idx+1]] = 0
    smat.eliminate_zeros()
    return smat

def sparse_multiply(a, b):
    assert isinstance(a, numpy.matrixlib.defmatrix.matrix)
    assert isinstance(b, numpy.matrixlib.defmatrix.matrix)
    # Only for this type do I have a guarantee that I wont
    # accidentally blow up the memory.
    assert a.shape == b.shape
    if a.shape[0] == 1:
        a1 = a.shape[1]
        return b * scipy.sparse.spdiags(a, 0, a1, a1)
    elif a.shape[1] == 1:
        a0 = a.shape[0]
        return scipy.sparse.spdiags(a, 0, a0, a0) * b
    else:
        raise ValueError((a,b))

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
        self.pa = Aggregator(
            datacfg=datacfg, ppcfg=ppcfg, expcfg=expcfg)

        with rasengan.tictoc('Init Part 1 : The Datacfg'):
            self.cp = DbfilenameShelf(
                r'%s/%s'%(uc.get_pfx(),self.datacfg.cp_fn),
                protocol=-1,
                flag='r')
            self.TM = self.cp['__TOKEN_MAPPER__']
            # self.TM.final must be patched to work with older
            # versions of TokenMapper that are in the pickle.
            if not hasattr(self.TM, 'final'):
                self.TM.final = False
            if self.is_malignull():
                self.TM([self.expcfg.NULL_KEY])
            self.bos_idx = self.TM.finalize()
            self.url_list = self.cp['__URL_LIST__']
            self.cat_folds = pkl.load(uc.proj_open(self.datacfg.fold_fn))
            self.cat2url = uc.load_cat2url(uc.proj_open(self.datacfg.cat2url_fn))
            self.url_to_idx = dict((b,a) for a,b in enumerate(self.url_list))
            pass

        with rasengan.tictoc('Init Part 2 : The PP CFG'):
            self.smat = io.mmread(uc.proj_open('catpeople_pp_%d'%args.ppcfg))
            if self.pp_prefix_is([UNIVEC, BIVEC, MALIGNER, DSCTOKVEC]):
                self.vectors = np.load(uc.proj_open('catpeople_pp_%d.vec'%args.ppcfg))
            pass

        if self.is_malignull():
            self.NULL_VEC = np.zeros((1,self.vectors.shape[1]))
        if self.exp_prefix_is([NBKERNEL, KERMACH, MALIGNER]):
            assert self.pp_prefix_is([UNIVEC, BIVEC, DSCTOKVEC])

        if self.expcfg.rm_fn_word:
            from rasengan.function_words import get_function_words
            self.fnwords = []
            for e in get_function_words():
                try:
                    self.fnwords.append(self.TM(e.lower()))
                except KeyError:
                    continue
            self.fnwords = set(self.fnwords)
            self.remove_fn_word() # Internally Manipulates smat
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
        column_idi = self.get_col_index_of_function_unigrams()
        if self.pp_prefix_is([UNIVEC, UNIGRAM, DSCTOK, DSCTOKVEC]):
            pass
        elif self.pp_prefix_is([BIVEC, BIGRAM]):
            column_idi.extend(self.get_col_index_of_function_bigrams())
        else:
            raise NotImplementedError(self.ppcfg._name)
        self.smat = set_column_of_sparse_matrix_to_zero(self.smat, column_idi)
        return

    def get_col_index_of_function_unigrams(self ):
        return self.fnwords

    def get_col_index_of_function_bigrams(self):
        fnwords = self.fnwords
        base = len(self.TM)
        l = []
        for ci in xrange(base, self.smat.shape[1]):
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
        self.pa(cat, scores, train_idx, test_idx)

    def __call__(self):
        print 'Total=', len(list(self.fold_iterator()))
        for cat, (train_idx, test_idx) in self.fold_iterator():
            self.call_impl(cat, train_idx, test_idx)
        return

    @staticmethod
    def get_top_occurring_col(mat, pct, reverse=False):
        colsum = mat.sum(axis=0)
        assert colsum.shape == (1, mat.shape[1])
        entities = mat.shape[0]
        threshold = (pct * entities)/100.0
        if reverse:
            return (colsum < threshold).nonzero()[1]
        else:
            return (colsum >= threshold).nonzero()[1]

    def keep_only_top_occurring_tokens(self, mat):
        bottom_col = self.get_top_occurring_col(mat, self.expcfg.top_token_pct, reverse=True)
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
            undesirable_columns.extend(topic.values())
        self.topics = topics
        return

    def extract_mode(self, problem, assignment):
        assert self.expcfg.malign_method == 'fast_align'
        assert self.expcfg.malign_kernel == 'cosine'
        return maligner.fast_relax(problem, assignment, self.expcfg)


    def fit(self, mat, train_idx):
        if self.expcfg.top_token_pct > 0:
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
        return [sparse_multiply(mat[i], w).sum()
                for i in xrange(mat.shape[0])]

    def score_nbkernel(self, mat):
        scorer = self.get_nbkernel_scorer()
        return [scorer(mat[i]) for i in xrange(mat.shape[0])]

    def score_malign(self, mat):
        scorer = self.get_malign_scorer()
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
        else:
            raise ValueError(self.expcfg.aggfn)

        def scorer(row):
            score = 0.0
            columns = list(row.nonzero()[1])
            if self.expcfg.kernel == 'vanilla':
                # Score = average over score of each topic.
                # Score of each topic = best score of topic with any token.
                score = np.dot(vectors, self.vectors[columns].T).max(axis=1).mean()
                # Score = average over score of each token.
                # Score of each topic = best score of topic with any token.
                # score = np.dot(vectors, self.vectors[columns].T).max(axis=0).mean()
                # ------------------------------ #
                # SLOW VERSION OF THE ABOVE CODE #
                # ------------------------------ #
                # for col in columns:
                #     vec = self.vectors[col]
                #     s = np.dot(vectors, vec).max()
                #     score += s
                return score
            elif self.expcfg.kernel == 'l2':
                raise NotImplementedError(self.expcfg.kernel)
            else:
                raise NotImplementedError(self.expcfg.kernel)

        return scorer

    def fold_iterator(self):
        for cat, folds in self.cat_folds.iteritems():
            url_in_cat = self.cat2url[cat]
            mapper = lambda lst : [self.url_to_idx[url_in_cat[i]] for i in lst]
            for fold_idx, fold in enumerate(folds):
                if fold_idx in self.expcfg.folds:
                    yield cat, (mapper(fold[0]), mapper(fold[1]))
            break

    def report(self):
        print self.pa

    def save_results(self, fn=None):
        if fn is None:
            fn = args.out_pkl_fn
        pkl.dump(self.pa, open(fn, 'wb'))

def main():
    rnr = ExperimentRunner(
        datacfg=DATACONFIG,
        ppcfg=CONFIG[args.ppcfg],
        expcfg=EXPCONFIG[args.expcfg],)
    rnr()
    rnr.save_results(fn=args.out_pkl_fn)
    rnr.report()

if __name__ == '__main__':
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
    with rasengan.debug_support():
        main()
#  Local Variables:
#  eval: (progn (anaconda-mode -1) (eldoc-mode -1) (company-mode -1) (linum-mode 1))
#  End:
