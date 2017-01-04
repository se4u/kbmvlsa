#!/usr/bin/env python
'''
| Filename    : lib_embed_entity.py
| Description : Create KB embedding
| Author      : Pushpendre Rastogi
| Created     : Sat Dec  3 11:20:45 2016 (-0500)
| Last-Updated: Wed Jan  4 14:53:38 2017 (-0500)
|           By: System User
|     Update #: 200
The `eval.py` file requires an embedding of the entities in the KB.
This library provides methods to embed entities. Typically these methods
will be called `offline` and their results will be accessed by `eval.py`
at runtime. The experiments naturally decouple, so the results from this
library will typically be stored on disk.
'''
import config
import lib_linalg
import numpy, sys, os
import scipy.sparse
import scipy.sparse.linalg
from sklearn.feature_extraction.text import TfidfTransformer
import sklearn.utils.validation
from sklearn.preprocessing import normalize
from class_composable_transform import ComposableTransform
from rasengan import tictoc, print_config

class MVLSA_WEIGHTING_ENUM(object):
    NONE = 'NONE'
    GLOVE = 'GLOVE'
    ARORA = 'ARORA'
    MVLSA = 'MVLSA'
    pass


def csr_or_csc(x):
    return (scipy.sparse.isspmatrix_csc(x)
            or scipy.sparse.isspmatrix_csr(x))

def clbl_sqrt(x):
    assert csr_or_csc(x), 'sqrt '+str(type(x))
    numpy.sqrt(x.data, out=x.data)
    return x

def clbl_log1p(x):
    assert csr_or_csc(x), 'log1p '+str(type(x))
    numpy.log1p(x.data, out=x.data)
    return x

def clbl_norm(x):
    assert csr_or_csc(x), 'norm '+str(type(x))
    r = normalize(x, norm='l2', axis=1, copy=False)
    if r is not x:
        del x
    return r


def myTfidfTransformer(X, use_idf):
    '''
    The formula that is used to compute the tf-idf of term t is
    tf-idf(d, t) = tf(t) * idf(d, t), and the idf is computed as
    idf(d, t) = log [ n / df(d, t) ]
    where n is the total number of documents and df(d, t) is the
    document frequency; the document frequency is the number of documents d
    that contain term t. Note that terms that occur in all documents
    in a training set, will be completely ignored.
    (Note that the idf formula above differs from the standard
    textbook notation that defines the idf as
    idf(d, t) = log [ n / (df(d, t) + 1) ]).
    '''
    assert scipy.sparse.isspmatrix_csc(X)
    n_samples, n_features = X.shape
    if use_idf:
        df = numpy.diff(X.indptr)
        idf = numpy.log(float(n_samples)/df)
        for i in xrange(n_features):
            X.data[X.indptr[i]:X.indptr[i+1]] *= idf[i]
        del df, idf
    return X

def clbl_tfidf(x):
    # if x is not y: del x
    return myTfidfTransformer(x, use_idf=True)

def clbl_tf(x):
    return myTfidfTransformer(x, use_idf=False)

# These callables modify input *INPLACE*
callables = dict(
    IDENTITY=(lambda _: _),  # pylint: disable=unnecessary-lambda
    SQROOT=clbl_sqrt,
    LOG   =clbl_log1p,
    # We don't copy data only if the original data was in `csr` format.
    # Otherwise, if the data was dense, or it was in csc format, we copy the data.
    TF   =clbl_tf,
    TFIDF=clbl_tfidf,
    NORM=clbl_norm,
)

VT = ComposableTransform(
    callables,
    set('NORM LOG SQROOT '
        'TFIDF TF '
        'NORM_TFIDF NORM_TF '
        'SQROOT_TFIDF LOG_TFIDF'.split()))
VTNS = VT.NS


def sparse_svd(arr, k, method='arpack', **kwargs):
    if method == 'arpack':
        return scipy.sparse.linalg.svds(arr, k=k, return_singular_vectors="u")
    if method == 'halko':
        return randomized_svd(arr, k, n_oversamples=10, n_iter=2, power_iteration_normalizer=None, transpose='auto', flip_sign=False, random_state=0)
    if method == 'svdlibc':
        from sparsesvd import sparsesvd
        return sparsesvd(arr, k)


def populate_remove_idx(remove_idx):
    return tuple([int(e) for e in remove_idx.split('.') if e != ''])

class Mvlsa(object):
    ''' The MVLSA procedure is a simple algorithm for creating the embedding of
    the entities of a knowledge graph. The `arr_list` is a list of arrays and
    `opt` is an instance of `MvlsaOption` that specifies the options of MVLSA.
    --- INPUT ---
    arr_list : A list of `sparse csr` numpy arrays. Note that this class modifies
               the arrays in place!
    opt      : An option object.
    --- OUTPUT ---
    emb  : An embedding of arr_list
    mask : A binary mask specifying the rows that were kept for mvlsa.
    '''
    def __init__(self, final_dim=300,
                 intermediate_dim=300,
                 view_transform=VTNS.TF,
                 row_weighting=MVLSA_WEIGHTING_ENUM.NONE,
                 mean_center=1,
                 regularization=1e-7,
                 remove_idx='',
                 svd_method='arpack',
                 **_kwargs):
        assert hasattr(VTNS, view_transform)
        # We don't really process the final_dim argument.
        self.final_dim = final_dim
        self.intermediate_dim = intermediate_dim
        self.regularization = regularization
        self.view_transform = view_transform
        self.row_weighting = row_weighting
        self.mean_center = mean_center
        self.remove_idx = populate_remove_idx(remove_idx)
        self.svd_method = svd_method
        return

    def create_AT(self, arr_gen, intmdt_fn=None):
        # TODO: Make a shortcut, it the array to be generated already exists
        try:
            I = arr_gen.I
        except AttributeError:
            I = arr_gen[0].shape[0]
        AT_arr_shape = (I, self.intermediate_dim*len(arr_gen))
        if intmdt_fn is None:
            print "Allocating array of size", AT_arr_shape
            AT_arr = numpy.empty(AT_arr_shape, dtype='float32', order='C')
        else:
            AT_arr = numpy.memmap(intmdt_fn, dtype='float32', mode='w+',
                                  shape=AT_arr_shape, order='C')
        transform_f = VT.parse(self.view_transform)
        for arr_idx, _arr in enumerate(arr_gen):
            # arr = numpy.asfortranarray(transform_f(_arr))
            arr_ = transform_f(_arr)
            arr = arr_.tocsc()
            if arr is not _arr:
                del _arr
            if arr is not arr_:
                del arr_
            print >> sys.stderr, arr_idx, arr.shape, arr.max(), arr.min()
            print_config(msg='Started SVDS')
            with tictoc('Timing SVD', override='stderr'):
                [A, S, B] = sparse_svd(arr, self.intermediate_dim,
                                       method=self.svd_method)
            print_config(msg='Finished SVDS')
            if self.mean_center:
                if B is not None:
                    [A, S, B] = lib_linalg.mean_center(A, S, B, arr)
                    del B
                else:
                    [A, S] = lib_linalg.mean_center(A, S, arr)
            A *= self.create_T(S)
            begin = self.intermediate_dim*arr_idx
            end = self.intermediate_dim*(arr_idx+1)
            AT_arr[:, begin:end] = A
            del A, S, B
            print_config(msg='Finished processing Array: '+str(arr_idx))
            if intmdt_fn is not None:
                AT_arr.flush()
        return AT_arr

    def create_T(self, S):
        assert S.ndim == 1
        T = (S / (S + self.regularization/2))[numpy.newaxis,:]
        return T

    def perform_inplace_row_weighting(self, AT_arr):
        # TODO: Perform row weighting
        return AT_arr

    def process_AT(self, AT_arr, debug=False):
        print_config(msg='Started svd_1')
        with tictoc('Performing Final SVD', override='stderr'):
            [G, i] = lib_linalg.svd_1(AT_arr, debug=debug)
        print_config(msg='Finished svd_1')
        return G

    def __call__(self, arr_gen, save_intmdt_fn=None, stage=1):
        AT_arr = self.create_AT(arr_gen, intmdt_fn=save_intmdt_fn)
        emb = self.process_AT(AT_arr)
        return emb


class ConcatLsa(object):
    def __init__(self):
        pass

    def __call__(self, data, stage=1):
        pass


class CscArrayGenerator(object):
    def __init__(self, I, fn=None, remove_idx='', **kwargs):
        self.fn = fn
        self.I = I
        self.remove_idx = populate_remove_idx(remove_idx)
        self._rep = 'CscArrayGenerator(%s)'%fn
        if fn is None:
            self.total_l = 3
        else:
            self.total_l = len(config.TREC_WEB_CATEGORIES)
        self.effective_l = len([e for e in range(self.total_l)
                                if e not in self.remove_idx])
        self.npz_data = None
        self.idx = 0

    def __repr__(self):
        return self._rep

    def next(self):
        while self.idx in self.remove_idx:
            self.idx += 1
        if self.idx >= self.total_l:
            raise StopIteration()
        mat = (self.next_random()
               if self.npz_data is None
               else self.next_fn())
        self.idx += 1
        return mat

    def next_random(self):
        return scipy.sparse.rand(self.I, 500, .4, 'csc').astype('float32')

    def next_fn(self):
        _indptr = self.npz_data['%d_indptr'%self.idx]
        _indptr.cumsum(out=_indptr)
        indptr = numpy.concatenate(([0], _indptr), axis=0)
        indices = numpy.asarray(self.npz_data['%d_indices'%self.idx])
        _data = self.npz_data['%d_data'%self.idx]
        data = _data.astype('float32')
        del _data, _indptr
        shape = (self.I, len(indptr) - 1)
        print >>sys.stderr, 'shape', shape, 'len(data)', len(data), \
            'len(indices)', len(indices)
        mat = scipy.sparse.csc_matrix((data, indices, indptr),
                                      shape=shape, dtype='float32')
        return mat

    def __iter__(self):
        if self.fn is not None:
            self.npz_data = numpy.load(self.fn)
        return self

    def __len__(self):
        return self.effective_l

    def __getitem__(self, idx):
        raise NotImplementedError()


def parse(arguments):
    '''
    Mvlsa := (final_dim~[num]@)?\
             (intemediate_dim~[num]@)?\
             (view_transform~[str]@)?\
             (row_weighting~[word]@)?\
             (mean_center~[01]@)?\
             (remove_idx~[num.+]@)?\
             (svd_method~[arpack|halko|svdlibc]@)?
    '''
    TYPES = dict(Mvlsa=dict(final_dim=int,
                            intermediate_dim=int,
                            mean_center=int,
                            view_transform=str,
                            row_weighting=str,
                            regularization=float,
                            remove_idx=str,
                            svd_method=str))
    def process(parent, tup):
        #print TYPES[parent], tup[0]
        return (tup[0], TYPES[parent][tup[0]](tup[1]))
    arguments = arguments.split('@')
    transformer = arguments[0]
    arguments = dict(process(transformer, e.split('~')) for e in arguments[1:])
    return transformer, arguments

def embed(arguments, I, fn, save_intmdt_fn=None):
    transformer, arguments = parse(arguments)
    arr_generator = CscArrayGenerator(I, fn=fn, **arguments)
    transformer = eval(transformer)
    return transformer(**arguments)(arr_generator, save_intmdt_fn=save_intmdt_fn)


'''
1. [X] I am leaking memory in some places.
       One possible way to figure this out is to do a line by line memory profiling
       with a smaller file. Instead I just checked the jobs where I took too much
       memory and then just reduced the memory of their code paths.
2. [X] I should memmap the large array, rather than creating it in memory.
   This way, I get an automatic backup while I am building the array.
3. The cpu_percent in psutils that I am using is wrong.
4. The program core dumped while processing SQRT and IDENTITY
   The memory usage was ~ 30% at RSS=80 and HWM=109, so there
   was no memory leak, but maybe I tried to delete something that
   did not exist? The things that did not core dump were TFIDF, TF, NORM_TF
   TFIDF = 140G, TF=NORM_TF=110G (It turns out that TF = Identity, so no biggy)
   So there was a memory leak with TFIDF ( I Fixed that)
5. The individual SVDs take a long time:
   6.2 ks, 3.0 ks, 4.3 ks, 1.0 ks, 11.7 ks, 3.0 ks, 10.8 ks = 40ks
   Perfect parallelization will decrease time to 11.7ks
   But the memory usage will increase, and if I am able to speed up
   the SVD 4 times, then I'll have the same effect.
   Fix: I have increased threads to 32, in the hope that that will increase
   my CPU utilization during the sparse SVD.
6. I should store the singular values to track how much energy I am throwing away.
7. I need to add methods for weighting the GCCA, weighted SVD is NP hard, but
   methods like ADAGrad can handle it.
8. I need to do mean normalization.
'''
if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int)
    arg_parser.add_argument('--config', type=str)
    arg_parser.add_argument('--I', default=config.TREC_WEB_N_ENTITIES, type=int)
    arg_parser.add_argument('--fn', default=config.TREC_WEB_HIT_LIST_NPZ, type=str)
    arg_parser.add_argument('--test', default=0, type=int)
    args=arg_parser.parse_args()
    import random
    random.seed(args.seed)
    numpy.random.seed(args.seed)
    out_fn = os.path.join(config.TREC_WEB_STORAGE, args.config)
    if args.test:
        args.fn = None
    G = embed(args.config, args.I, args.fn,
              save_intmdt_fn=out_fn+'.AT_arr')
    with tictoc('Pickling G'):
        with open(out_fn, 'wb') as f:
            numpy.save(f, G, allow_pickle=False)
