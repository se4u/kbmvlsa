#!/usr/bin/env python
import cPickle, sys
with open(sys.argv[1]) as f:
    data = cPickle.load(f)
import numpy as np
data2 = np.load(open(sys.argv[2]), allow_pickle=False)
assert zip((data2)['0_indices'][:data2['0_indptr'][0]], (data2)['0_data'][:data2['0_indptr'][0]]) \
 == [(29, 1), (30, 1), (31, 1), (32, 1), (33, 1), (34, 1)]
print "Test passing"
