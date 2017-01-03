#!/usr/bin/env python
'''
| Filename    : lib_embed_entity.py
| Description : Create KB embedding
| Author      : Pushpendre Rastogi
| Created     : Sat Dec  3 11:20:45 2016 (-0500)
| Last-Updated: Tue Jan  3 10:22:01 2017 (-0500)
|           By: System User
|     Update #: 117
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
from numpy import sqrt, log1p  # pylint: disable=no-name-in-module
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import normalize
from class_composable_transform import ComposableTransform
from rasengan import tictoc
AT_arr = None

class MVLSA_WEIGHTING_ENUM(object):
    NONE = 'NONE'
    GLOVE = 'GLOVE'
    ARORA = 'ARORA'
    MVLSA = 'MVLSA'
    pass


# These callables modify input *INPLACE*
callables = dict(
    IDENTITY=(lambda _: _),
    SQROOT=(lambda x: sqrt(x, out=x)), # pylint: disable=unnecessary-lambda
    LOG  =(lambda x: log1p(x, out=x)),
    # We don't copy data only if the original data was in `csr` format.
    # Otherwise, if the data was dense, or it was in csc format, we copy the data.
    TF   =(lambda x: TfidfTransformer(norm=None, use_idf=False, sublinear_tf=False).fit(x).transform(x, copy=False)),
    TFIDF=(lambda x: TfidfTransformer(norm=None, use_idf=True, sublinear_tf=False).fit(x).transform(x, copy=False)),
    NORM=(lambda x: normalize(x, norm='l2', axis=1, copy=False)),
    # PMI=(lambda x: PmiTransformer()),
)

VT = ComposableTransform(
    callables,
    set('NORM IDENTITY LOG SQROOT '
        'TFIDF TF '
        'NORM_TFIDF NORM_TF '
        'SQROOT_TFIDF LOG_TFIDF'.split()))
VTNS = VT.NS

def print_config(msg=None, numpy=0, hostname=1, ps=1):
    try:
        if numpy:
            numpy.show_config()
        pid = os.getpid()
        if msg is not None:
            print msg
        print 'pid', pid
        import subprocess
        cmd = ("ps uf %d;"%pid if ps else "")
        cmd += " grep '[TV][hm][rHRS][eSWw]' /proc/%d/status; "%pid
        if hostname:
            cmd += "echo hostname `hostname`"
        print subprocess.check_output(
            [cmd],
            stderr=subprocess.STDOUT,
            shell=True)
    except:
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
        return

    def create_AT(self, arr_gen):
        global AT_arr
        # TODO: Make a shortcut, it the array to be generated already exists
        try:
            I = arr_gen.I
        except AttributeError:
            I = arr_gen[0].shape[0]
        AT_arr_shape = (I, self.intermediate_dim*len(arr_gen))
        print "Allocating array of size", AT_arr_shape
        AT_arr = numpy.empty(AT_arr_shape, dtype='float32')
        transform_f = VT.parse(self.view_transform)
        for arr_idx, _arr in enumerate(arr_gen):
            # arr = numpy.asfortranarray(transform_f(_arr))
            arr = transform_f(_arr)
            if not (arr is _arr):
                del _arr
                print "deleted _arr"
            print >> sys.stderr, arr_idx, arr.shape
            assert scipy.sparse.isspmatrix(arr), "Array number: " + str(arr_idx)
            assert scipy.sparse.isspmatrix_csc(arr), \
                "Array number: %d has type %s"%(arr_idx, str(type(arr)))
            print_config(msg='Started SVDS')
            with tictoc('Timing SVD'):
                [A, S, B] = scipy.sparse.linalg.svds(arr, k=self.intermediate_dim,
                                                     return_singular_vectors="u")
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

    def __call__(self, arr_gen, stage=1):
        AT_arr = self.create_AT(arr_gen)
        with open(OUT_FN+'.AT_arr', 'wb') as f:
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
    '''
    TYPES = dict(Mvlsa=dict(final_dim=int,
                            intermediate_dim=int,
                            mean_center=int,
                            view_transform=str,
                            row_weighting=str,
                            regularization=float,
                            remove_idx=str))
    def process(parent, tup):
        #print TYPES[parent], tup[0]
        return (tup[0], TYPES[parent][tup[0]](tup[1]))
    arguments = arguments.split('@')
    transformer = arguments[0]
    arguments = dict(process(transformer, e.split('~')) for e in arguments[1:])
    return transformer, arguments

def embed(arguments, I, fn, slice_by_I=0):
    transformer, arguments = parse(arguments)
    arr_generator = CscArrayGenerator(fn, I, slice_by_I=slice_by_I, **arguments)
    transformer = eval(transformer)
    return transformer(**arguments)(arr_generator)


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
    G = embed(args.config, args.I, args.fn, slice_by_I=args.slice_by_I)
    OUT_FN = os.path.join(config.TREC_WEB_STORAGE, args.config)
    with open(OUT_FN, 'wb') as f:
        numpy.save(f, G, allow_pickle=False)
