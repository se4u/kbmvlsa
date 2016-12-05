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
class MvlsaOption(object):
    def __init__(self, final_dim=50, intermediate_dim=100, view_transform=):

        pass
    def __str__(self):
        pass

def mvlsa(arr_list, opt):
    '''
    --- INPUT ---
    arr_list :
    opt      :
    --- OUTPUT ---
    emb      : An embedding of the
    desc     :
    '''
    pass

def concatLSA(arr_list, opt):
    pass

def gaussianEmbedding(arr_list, opt):
    d
