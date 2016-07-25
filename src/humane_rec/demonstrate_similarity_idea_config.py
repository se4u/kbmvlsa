#!/usr/bin/env python
'''
| Filename    : demonstrate_similarity_idea_config.py
| Description : A config file to hold demo algorithm configurations.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 23:34:29 2016 (-0400)
| Last-Updated: Mon Jul 25 02:34:43 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 22
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

    ''' When called this function object returns "True"
    if we have converged.
    '''

    def __init__(self, max_iter=10):
        self.max_iter = max_iter
        self._call_count = 0

    def __call__(self, _blfs):
        ret = (self._call_count >= self.max_iter)
        self._call_count += 1
        return ret


class Fixed_L2_Belief_Tolerance_Convergence(object):

    def __init__(self, min_iter=10, avg_tol=1e-6):
        self.min_iter = min_iter
        self.avg_tol = avg_tol
        self.prev_blfs = None
        self._call_count = 0

    def __call__(self, blfs):
        self._call_count += 1
        if self._call_count < self.min_iter:
            self.prev_blfs = blfs
            return False
        else:
            dist = self.distance(self.prev_blfs, blfs)
            self.prev_blfs = blfs
            return (dist < self.avg_tol)

    def distance(self, prev_blfs, blfs):
        return numpy.sqrt(sum(numpy.linalg.norm(pb - b)**2
                              for (pb, b)
                              in zip(prev_blfs, blfs)) / len(blfs))


# -------------- #
# Configure Demo #
# -------------- #
introduce_NULL_embedding = True
NULL_KEY = '--NULL--'
demo_second_mode = False
demo_third_mode = False
demo_fourth_mode = False
demo_fifth_mode = False
first_mode_tags_to_remove = {
    'Condoleezza_Rice': 'book',
    'Carly_Fiorina': 'book',
    'Geraldine_Ferraro': 'lost',
    'Elizabeth_Smart': 'took',
    'Hillary_Rodham_Clinton': 'book',
    'Judy_Woodruff': 'took',
    'Martha_Stewart': 'book'}
second_mode_tags_to_remove = {
    'Condoleezza_Rice': 'quoted',
    'Carly_Fiorina': 'told',
    'Geraldine_Ferraro': 'speak',
    'Elizabeth_Smart': 'speech',
    'Hillary_Rodham_Clinton': 'speech',
    'Judy_Woodruff': 'interview',
    'Martha_Stewart': 'words'}
third_mode_tags_to_remove = {
    'Condoleezza_Rice': 'published',
    'Carly_Fiorina': 'claimed',
    'Geraldine_Ferraro': 'said',
    'Elizabeth_Smart': 'described',
    'Hillary_Rodham_Clinton': 'wrote',
    'Judy_Woodruff': 'interview',
    'Martha_Stewart': 'published'}
fourth_mode_tags_to_remove = {
    'Condoleezza_Rice': 'secretary',
    'Carly_Fiorina': 'senate',
    'Geraldine_Ferraro': 'representative',
    'Elizabeth_Smart': 'keynote',
    'Hillary_Rodham_Clinton': 'secretary',
    'Judy_Woodruff': 'correspondent',
    'Martha_Stewart': 'presenter'}

# -------------------- #
# Configure Fast_Relax #
# -------------------- #
fast_relax.node_pick_policy = Sequential_Policy()
fast_relax.respect_initial_assignment_for_initializing_beliefs = True
fast_relax.has_converged = Fixed_Iter_Convergence(50)
# fast_relax.has_converged = Fixed_L2_Belief_Tolerance_Convergence(10, 1e-6)
fast_relax.verbose = True
