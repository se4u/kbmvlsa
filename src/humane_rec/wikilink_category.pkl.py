#!/usr/bin/env python
'''
| Filename    : wikilink_category.pkl.py
| Description : Convert flat files that contain categories of links to a single dict
| Author      : Pushpendre Rastogi
| Created     : Tue Jul 12 18:39:04 2016 (-0400)
| Last-Updated: Tue Jul 12 19:00:18 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 4
'''
import sys
import os
import pickle
from rasengan import pivot_key_to_list_map_by_item
in_dir = sys.argv[1]
out_pkl_fn = sys.argv[2]
b = len('"Category:')
link_to_category = dict((f, [e.strip()[b:-1] for e in open(in_dir + os.sep + f)])
                        for f in os.listdir(in_dir))
with open(out_pkl_fn, 'wb') as f:
    pickle.dump(
        dict(category_to_link=pivot_key_to_list_map_by_item(link_to_category),
             link_to_category=link_to_category),
        f)
