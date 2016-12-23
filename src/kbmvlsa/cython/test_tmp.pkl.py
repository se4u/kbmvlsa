#!/usr/bin/env python
'''
| Filename    : test_tmp.pkl.py
| Description : A test of the tmp.pkl file
| Author      : Pushpendre Rastogi
| Created     : Fri Dec 23 17:19:56 2016 (-0500)
| Last-Updated: Fri Dec 23 17:30:04 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 5
'''
import cPickle
with open("/tmp/tmp.pkl") as f:
    data = cPickle.load(f)

assert len(data) == len(["DOCNO", "DOCHDR", "names", "category", "attributes",
                          "SimEn", "RelEn"])
assert data[5]['carmela'] == 2
assert data[0]['destroy-oh-boy'] == 1
assert data[6]['footloose'] == 2
print "Passed Test"
