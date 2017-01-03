#!/usr/bin/env python
'''
| Filename    : lib_embed_entity.py
| Description : Create KB embedding
| Author      : Pushpendre Rastogi
| Created     : Sat Dec  3 11:20:45 2016 (-0500)
| Last-Updated: Tue Jan  3 16:13:34 2017 (-0500)
|           By: System User
|     Update #: 162
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
from rasengan import tictoc

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


class MyTfidfTransformer(TfidfTransformer):
    def transform(self, X, copy=False):
        assert not copy
        n_samples, n_features = X.shape
        if self.sublinear_tf or self.norm:
            raise NotImplementedError()
        if self.use_idf:
            sklearn.utils.validation.check_is_fitted(
                self, '_idf_diag', 'idf vector is not fitted')
            assert n_features == self._idf_diag.shape[0]
            for i in xrange(X.shape[1]):
                X.data[X.indptr[i]:X.indptr[i+1]] *= self._idf_diag.data[i]
        return X

def clbl_tfidf(x):
    y = MyTfidfTransformer(norm=None, use_idf=True, sublinear_tf=False).fit(x).transform(x, copy=False)
    if x is not y:
        del x
    return y

def clbl_tf(x):
    y = MyTfidfTransformer(norm=None, use_idf=False, sublinear_tf=False).fit(x).transform(x, copy=False)
    if x is not y:
        del x
    return y

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
    set('NORM IDENTITY LOG SQROOT '
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

def print_config(msg=None, numpy=0, hostname=1, ps=1):
    try:
        if numpy:
            numpy.show_config()
        if msg is not None:
            print msg
        if hostname:
            import socket
            print 'hostname', socket.gethostname()
        pid = os.getpid()
        print 'pid', pid
        proc_stat = dict(e.strip().split(':') for e in open('/proc/%d/status'%pid))
        print 'VmHWM', proc_stat["VmHWM"]
        print 'VmRSS', proc_stat["VmRSS"]
        print 'VmSwap', proc_stat["VmSwap"]
        print 'Threads', proc_stat["Threads"]
        import psutil
        p = psutil.Process(pid)
        print 'CPU%        ',  '%1.2f%%'%p.cpu_percent(interval=None)
        print 'MEM%        ', '%1.2f%%'%p.memory_percent()
    except Exception as e:
        print e
        pass
    return

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
                 view_transform=VTNS.IDENTITY,
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

    def create_AT(self, arr_gen):
        # TODO: Make a shortcut, it the array to be generated already exists
        try:
            I = arr_gen.I
        except AttributeError:
            I = arr_gen[0].shape[0]
        AT_arr_shape = (I, self.intermediate_dim*len(arr_gen))
        print "Allocating array of size", AT_arr_shape
        try:
            AT_arr = numpy.empty(AT_arr_shape, dtype='float32')
        except MemoryError:
            AT_arr = None
        transform_f = VT.parse(self.view_transform)
        for arr_idx, _arr in enumerate(arr_gen):
            # arr = numpy.asfortranarray(transform_f(_arr))
            arr_ = transform_f(_arr)
            if arr_ is not _arr: del _arr
            arr = arr_.tocsc()
            if arr is not arr_: del arr_
            print >> sys.stderr, arr_idx, arr.shape
            assert scipy.sparse.isspmatrix(arr), "Array number: " + str(arr_idx)
            assert scipy.sparse.isspmatrix_csc(arr), \
                "Array number: %d has type %s"%(arr_idx, str(type(arr)))
            print_config(msg='Started SVDS')
            with tictoc('Timing SVD'):
                print arr.max(), arr.min()
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
        [G, i] = lib_linalg.svd_1(AT_arr, debug=debug)
        print_config(msg='Finished svd_1')
        return G

    def __call__(self, arr_gen, save_intmdt_fn=None, stage=1):
        AT_arr = self.create_AT(arr_gen)
        if save_intmdt_fn is not None:
            with open(save_intmdt_fn, 'wb') as f:
                numpy.save(f, AT_arr, allow_pickle=False)
        emb = self.process_AT(AT_arr)
        return emb


class ConcatLsa(object):
    def __init__(self):
        pass

    def __call__(self, data, stage=1):
        pass


class CscArrayGenerator(object):
    def __init__(self, fn, I, remove_idx='', slice_by_I = 0, **kwargs):
        self.fn = fn
        self.I = I
        self.remove_idx = populate_remove_idx(remove_idx)
        self._rep = 'CscArrayGenerator(%s)'%fn
        self.total_l = len(config.TREC_WEB_CATEGORIES)
        self.effective_l = len([e for e in range(self.total_l) if e not in self.remove_idx])
        self.npz_data = None
        self.idx = 0
        self.slice_by_I = slice_by_I

    def __repr__(self):
        return self._rep

    def next(self):
        while self.idx in self.remove_idx:
            self.idx += 1
        if self.idx >= self.total_l:
            raise StopIteration()
        _indptr = self.npz_data['%d_indptr'%self.idx]
        _indptr.cumsum(out=_indptr)
        indptr = numpy.concatenate(([0], _indptr), axis=0)
        indices = numpy.asarray(self.npz_data['%d_indices'%self.idx])
        _data = self.npz_data['%d_data'%self.idx]
        data = _data.astype('float32')
        del _data, _indptr
        if self.slice_by_I:
            indptr = indptr[:self.I+1]
            data = data[:indptr[-1]]
            indices = indices[:indptr[-1]]
        shape = (self.I, len(indptr) - 1)
        print >>sys.stderr, 'shape', shape, 'len(data)', len(data), \
            'len(indices)', len(indices)
        self.idx += 1
        mat = scipy.sparse.csc_matrix((data, indices, indptr), shape=shape, dtype='float32')
        return mat

    def __iter__(self):
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

def embed(arguments, I, fn, slice_by_I=0, save_intmdt_fn=None):
    transformer, arguments = parse(arguments)
    arr_generator = CscArrayGenerator(fn, I, slice_by_I=slice_by_I, **arguments)
    transformer = eval(transformer)
    return transformer(**arguments)(arr_generator, save_intmdt_fn=save_intmdt_fn)


if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int)
    arg_parser.add_argument('--config', type=str)
    arg_parser.add_argument('--I', default=config.TREC_WEB_N_ENTITIES, type=int)
    arg_parser.add_argument('--fn', default=config.TREC_WEB_HIT_LIST_NPZ, type=str)
    arg_parser.add_argument('--slice_by_I', default=0, type=int)
    args=arg_parser.parse_args()
    import random
    random.seed(args.seed)
    numpy.random.seed(args.seed)
    out_fn = os.path.join(config.TREC_WEB_STORAGE, args.config)
    G = embed(args.config, args.I, args.fn,
              slice_by_I=args.slice_by_I,
              save_intmdt_fn=out_fn+'.AT_arr')
    with open(out_fn, 'wb') as f:
        numpy.save(f, G, allow_pickle=False)
