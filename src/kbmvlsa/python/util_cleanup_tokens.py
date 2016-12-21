#!/usr/bin/env python
'''
| Filename    : util_cleanup_tokens.py
| Description : Receive tokens on stdin and produce a list of clean tokens on stdout
| Author      : Pushpendre Rastogi
| Created     : Sun Dec 11 18:21:13 2016 (-0500)
| Last-Updated: Sun Dec 11 19:41:37 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 10
'''
import re
import krovetzstemmer
from string import maketrans
import sys
stemmer = krovetzstemmer.Stemmer().stem
PUNCT_CHAR = frozenset(''.join(chr(e) for e in range(
    33, 48) + range(58, 65) + range(91, 97) + range(123, 127)))
REGEX_SPECIAL_CHAR = frozenset(r'[]().-|^{}*+$\?')
keep = False
keep_or_remove_punct = ('([%s])' if keep else '[%s]')
PUNCT_MATCH_REGEX = re.compile(
    keep_or_remove_punct%(''.join(
        ('\\%s'%e if e in REGEX_SPECIAL_CHAR else e)
        for e in PUNCT_CHAR)))
num2zero_table = maketrans("0123456789", "0000000000")
for row in sys.stdin:
    row = row.strip()
    if row != '':
        print row,
        for e in re.split(PUNCT_MATCH_REGEX, row.lower().translate(None, ".")):
            if e != '':
                print (stemmer(e).translate(num2zero_table) if len(e) > 3 else e),
        print
