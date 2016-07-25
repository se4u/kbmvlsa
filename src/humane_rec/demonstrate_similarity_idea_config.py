#!/usr/bin/env python
'''
| Filename    : demonstrate_similarity_idea_config.py
| Description : A config file to hold demo algorithm configurations.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 23:34:29 2016 (-0400)
| Last-Updated: Mon Jul 25 00:42:42 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 3
'''
from rasengan import Namespace
import numpy
import numpy.linalg
fast_relax = Namespace()


class Sequential_Policy(object):

    def __init__(self):
        self.prev_call = -1

    def __call__(self, max):
        ret = (self.prev_call + 1) % max
        self.prev_call = ret
        return ret


class Fixed_Iter_Convergence(object):

    def __init__(self, max_iter=10):
        self.max_iter = max_iter
        self._call_count = 0

    def __call__(self, _blfs):
        ret = (self._call_count < self.max_iter)
        self._call_count += 1
        return ret


class Fixed_L2_Belief_Tolerance_Convergence(object):

    def __init__(self, min_iter=10, avg_tol=1e-6):
        self.min_iter = min_iter
        self.avg_tol = avg_tol
        self.prev_blfs = None
        self._call_count = 0

    def __call__(self, blfs):
        call_count_criterion = (self._call_count < self.min_iter)
        self._call_count += 1
        if call_count_criterion:
            self.prev_blfs = blfs
            return True
        else:
            dist = self.distance(self.prev_blfs, blfs)
            self.prev_blfs = blfs
            return (dist > self.avg_tol)

    def distance(self, prev_blfs, blfs):
        return numpy.sqrt(sum(numpy.linalg.norm(pb - b)**2
                              for (pb, b)
                              in zip(prev_blfs, blfs)) / len(blfs))

fast_relax.node_pick_policy = Sequential_Policy()
fast_relax.respect_initial_assignment_for_initializing_beliefs = True
fast_relax.has_converged = Fixed_Iter_Convergence(10)
# fast_relax.has_converged = Fixed_L2_Belief_Tolerance_Convergence(10, 1e-6)
