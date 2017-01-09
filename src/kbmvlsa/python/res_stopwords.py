#!/usr/bin/env python
'''
| Filename    : res_indri_stopword_list.py
| Description : Standard Indri Stopword List
| Author      : Pushpendre Rastogi
| Created     : Sun Dec  4 23:29:12 2016 (-0500)
| Last-Updated: Tue Dec 20 17:38:02 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 6
This file provides a `STOP_WORDS` list, that is a combination
of two stop words lists, one from `Indri` and the second from
the Glasgow IR group.
Glasgow: ir.dcs.gla.ac.uk/resources/linguistic_utils/stop_words
Indri  : www.lemurproject.org/stopwords/stoplist.dft
'''
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
INDRI_STOP_WORDS = [e.strip() for e in open('../res/indri_stop_words.txt')]
STOP_WORDS = frozenset(INDRI_STOP_WORDS + list(ENGLISH_STOP_WORDS))
# print len(__INDRI_STOP_WORDS), len((ENGLISH_STOP_WORDS)), len(STOP_WORDS)
# 418 318 483
