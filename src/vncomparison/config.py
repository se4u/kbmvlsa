'''
| Filename    : config.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Feb 22 12:22:19 2016 (-0500)
| Last-Updated: Mon Feb 22 12:24:47 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 1
'''
import os
op = os.path
BASE_DIR = op.expanduser('~/Dropbox/paper/kbvn/')
DATA_DIR = op.join(BASE_DIR, "no_repo/data")
us_president_fn = op.join(DATA_DIR, "us-presidents.rdf/us-presidents.rdf")
