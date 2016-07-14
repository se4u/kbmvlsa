#!/usr/bin/env python
'''
| Filename    : util_sgm_span.py
| Description : Given a sgm file path and a span print the string around that span.
| Author      : Pushpendre Rastogi
| Created     : Wed Jul 13 14:48:48 2016 (-0400)
| Last-Updated: Thu Jul 14 01:59:03 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 61
'''

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from config import ACE, sanitize_doc, sanitize_doc_inverse
import sys
import os

fn = sys.argv[1]
start = int(sys.argv[2])
stop = int(sys.argv[3])
try:
    f = open(fn, encoding='utf-8')
except:
    f = open(os.path.join(ACE, fn), encoding='utf-8')

doc = BeautifulSoup(sanitize_doc(f.read()), 'html5lib')
elem_iter = doc.doc.next_elements
text = [sanitize_doc_inverse(e.output_ready())
        for e in elem_iter
        if isinstance(e, NavigableString)]
print (text)
text = ''.join(text)
print(text[start: stop + 1])
