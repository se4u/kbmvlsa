#!/usr/bin/env python
'''
| Filename    : rescal_relational_bbn2.py
| Description : Rescal on BBN2
| Author      : Pushpendre Rastogi
| Created     : Sat Apr 30 22:25:16 2016 (-0400)
| Last-Updated: Sat Apr 30 22:27:25 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 1
'''
import random
import numpy as np
import cPickle as pkl
from scipy.sparse import csc_matrix
import scipy
import rasengan
from collections import Counter
from rasengan import rank_metrics
import os
import ipdb as pdb
import igraph
import argparse
import itertools
