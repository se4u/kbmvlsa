#!/usr/bin/env python
'''
| Filename    : lib_embed_entity.py
| Description : Create KB embedding
| Author      : Pushpendre Rastogi
| Created     : Sat Dec  3 11:20:45 2016 (-0500)
| Last-Updated: Sun Dec  4 16:34:26 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 1
The `eval.py` file requires an embedding of the entities in the KB.
This library provides methods to embed entities. Typically these methods
will be called `offline` and their results will be accessed by `eval.py`
at runtime. The experiments naturally decouple, so the results from this
library will typically be stored on disk.
'''
from lib_view_transform import VT, VTNS
from lib_linalg import incremental_pca_update
MVLSA_WEIGHTING_ENUM = Exception()
for e in ['NONE', 'GLOVE', 'ARORA', 'MVLSA']:
    setattr(MVLSA_WEIGHTING_ENUM, e, e)

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
    def __init__(self, final_dim=50,
                 intermediate_dim=100,
                 view_transform=VTNS.IDENTITY,
                 row_weighting=MVLSA_WEIGHTING_ENUM.NONE,
                 mean_center=True):
        assert hasattr(VTNS, view_transform)
        self.final_dim = final_dim
        self.intermediate_dim = intermediate_dim
        self.view_transform = view_transform
        self.row_weighting = row_weighting
        self.mean_center = mean_center
        return

    def preprocess(self, arr_list):
        transform_f = VT.parse(self.view_transform)
        arr_list = [transform_f(arr) for arr in arr_list]
        return

    def create_AT(self, arr_list):
        AT_list = []
        for arr in arr_list:
            if self.mean_center:
                [A, S, B] = sparse_svd(arr, self.intermediate_dim, create_rsv=True)
                [A, S] = rank_one_svd_update(A, S, B, mean)
            else:
                [A, S] = sparse_svd(arr, self.intermediate_dim)
            T = self.create_T(S)
            AT_list.append(np.dot(A, T))
        return AT_list

    def perform_inplace_row_weighting(self, AT):
        # TODO: Perform row weighting
        return AT

        # ajtj_row = 0;
        # for i = 1:length(deptoload)
        #     ajtj_size = size(matfile(deptoload{i}), 'ajtj');
        #     load(deptoload{i}, 'kj_diag');
        #     ajtj_row = ajtj_size(1);
        #     if isnan(K)
        #         K = zeros(ajtj_size(1), 1);
        #     end
        #     K = K+kj_diag;
        # end;
        # ajtj = ajtj(logical_acceptable_rows,1:min(M, end));
        # assert(sanity_check_matrix(ajtj));
        # ajtj = spdiags(K.^(-1/2), 0, length(K), length(K))*ajtj;
        # assert(sanity_check_matrix(ajtj));


    def process_AT(self, AT_list):
        G = None
        S_tilde = None
        for AT in AT_list:
            self.perform_inplace_row_weighting(AT)
            incremental_pca_update(AT, G, S_tilde)
        return [G, S_tilde]

    def __call__(self, data, stage=1):
        assert stage in [1, 2, 3]
        if stage <= 1:
            data = self.preprocess(data)
        if stage <= 2:
            data = self.create_AT(data)
        if stage <= 3:
            emb, _ = self.process_AT(data)
        return emb





def concatLSA(arr_list, opt):
    pass

def gaussianEmbedding(arr_list, opt):
    pass
