#!/usr/bin/env python
'''
| Filename    : entity_to_string_pkl.py
| Description : Pkl the file entities_with_canonical_strings_and_their_strings
| Author      : Pushpendre Rastogi
| Created     : Fri Mar 11 00:09:12 2016 (-0500)
| Last-Updated: Fri Mar 11 00:27:46 2016 (-0500)
|           By: System User
|     Update #: 2
'''
import cPickle as pkl

d = {}
for row in open('entities_with_canonical_strings_and_their_strings'):
    row = row.strip()
    eid = row[:36]
    s = row[37:]
    d[eid] = s
with open('entity_to_string.pkl', 'wb') as f:
    pkl.dump(d, f)
