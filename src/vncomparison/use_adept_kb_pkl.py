#!/usr/bin/env python

import cPickle as pkl
data = pkl.load(open('../../res/adept.pkl'))
print data.keys()
print 'Total Nodes=', len(data['entity_to_int_map'])
total = 0
for idx, k in enumerate(data['data_dict']):
    l = len(data['data_dict'][k])
    print '%-3d'%idx, '%-60s'%k, l
    total += l
print 'Total Edges=', total
