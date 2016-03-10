'''
| Filename    : config.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Feb 22 12:22:19 2016 (-0500)
| Last-Updated: Tue Mar  8 18:39:07 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
import os
op = os.path
ope = op.expanduser
BASE_DIR = ope('~/Dropbox/paper/kbvn/')
DATA_DIR = op.join(BASE_DIR, "no_repo/data")
us_president_fn = op.join(DATA_DIR, "us-presidents.rdf/us-presidents.rdf")
adept_base_fn = ope('~/data/Adept/adept-kb/src/main/resources/adept/ontology/'
                    'adept-base.ttl')
adept_core_fn = ope('~/data/Adept/adept-kb/src/main/resources/adept/ontology/'
                    'adept-core.ttl')
