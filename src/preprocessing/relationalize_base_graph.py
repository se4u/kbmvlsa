#!/usr/bin/env python
'''
| Filename    : relationalize_base_graph.py
| Description : Convert the data in sort_base into a relational format with people as pkey and features
| Author      : Pushpendre Rastogi
| Created     : Wed Apr 13 18:52:57 2016 (-0400)
| Last-Updated: Thu Apr 14 12:08:04 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 8
'''
import yaml
from pprint import pprint
pprint(yaml.load(open('relationalize_base_graph.yaml').read()))
