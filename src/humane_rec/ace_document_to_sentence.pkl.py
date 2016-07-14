#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : tmp_beautifulsoup.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 10 16:51:25 2016 (-0400)
| Last-Updated: Thu Jul 14 02:44:11 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 68
Split by tag -> para -> sentence. Keep the delimiters at every step and
then mark the beginning and end of everything.
'''
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from config import ACE, sanitize_doc, sanitize_doc_inverse
import os
from collections import defaultdict
import sys
import pickle
import re
import nltk
import rasengan
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer._params.abbrev_types.update(
    ['e.j', 'u.s', 'b.p'])
tokenizer._params.collocations.update(
    [('lt', 'governor'), ('mt', 'everest'), ('j.d', 'hayworth'), ('j.d', 'baldwin')])
out_pkl_fn = sys.argv[1]
d = defaultdict(list)
blob_to_para = re.compile('(\n\n)')
for fn in [_ for _ in os.listdir(ACE) if _.endswith('.sgm')]:
    f_data = sanitize_doc(open(os.path.join(ACE, fn), encoding='utf-8').read())
    offset = 0
    for blob in BeautifulSoup(f_data, 'html5lib').doc.next_elements:
        if isinstance(blob, NavigableString):
            paras = blob_to_para.split(blob.output_ready())
            for para in paras:
                spans = tokenizer.span_tokenize(para)
                for span_start, span_end in spans:
                    d[fn].append(
                        [offset + span_start,
                         offset + span_end,
                         sanitize_doc_inverse(para[span_start:span_end])])
                offset += len(para)
        elif isinstance(blob, Tag) and blob.name == 'quote':
            offset += 0

with open(out_pkl_fn, 'wb') as f:
    pickle.dump(dict(d), f)
