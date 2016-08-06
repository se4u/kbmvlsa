#!/usr/bin/env python
'''
| Filename    : demonstrate_similarity_idea_config.py
| Description : A config file to hold demo algorithm configurations.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 23:34:29 2016 (-0400)
| Last-Updated: Fri Aug  5 18:49:25 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 41
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
use_big_tag_set = True
introduce_NULL_embedding = True
NULL_KEY = '--NULL--'
demo_second_mode = True
demo_third_mode = True
demo_fourth_mode = True
demo_fifth_mode = True
demo_sixth_mode = True
demo_seventh_mode = True
demo_eighth_mode = True
demo_nineth_mode = True
# first_mode_tags_to_remove = {
#     'Condoleezza_Rice': 'book',
#     'Carly_Fiorina': 'book',
#     'Geraldine_Ferraro': 'lost',
#     'Elizabeth_Smart': 'took',
#     'Hillary_Rodham_Clinton': 'book',
#     'Judy_Woodruff': 'took',
#     'Martha_Stewart': 'book'}
first_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'a', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'served', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'served', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'served', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'served', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'served', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'a'
}
# second_mode_tags_to_remove = {
#     'Condoleezza_Rice': 'quoted',
#     'Carly_Fiorina': 'told',
#     'Geraldine_Ferraro': 'speak',
#     'Elizabeth_Smart': 'speech',
#     'Hillary_Rodham_Clinton': 'speech',
#     'Judy_Woodruff': 'interview',
#     'Martha_Stewart': 'words'}
second_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'did', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'years', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'years', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'years', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'years', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'years', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'age'
}
# third_mode_tags_to_remove = {
#     'Condoleezza_Rice': 'published',
#     'Carly_Fiorina': 'claimed',
#     'Geraldine_Ferraro': 'said',
#     'Elizabeth_Smart': 'described',
#     'Hillary_Rodham_Clinton': 'wrote',
#     'Judy_Woodruff': 'interview',
#     'Martha_Stewart': 'published'}
third_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'born', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'died', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'born', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'elected', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'born', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'died', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'wife'
}
# fourth_mode_tags_to_remove = {
#     'Condoleezza_Rice': 'secretary',
#     'Carly_Fiorina': 'senate',
#     'Geraldine_Ferraro': 'representative',
#     'Elizabeth_Smart': 'keynote',
#     'Hillary_Rodham_Clinton': 'secretary',
#     'Judy_Woodruff': 'correspondent',
#     'Martha_Stewart': 'presenter'}
fourth_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'announced', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'released', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'going', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'announced', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'released', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'going', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'man'
}
fifth_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'interview', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'took', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'took', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'took', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'had', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'had', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'took'
}
sixth_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'left', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'time', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'time', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'time', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'is', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'is', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'time'
}
seventh_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'event', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'campaign', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'campaign', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'campaign', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'stood', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'campaign', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'stand'
}
eighth_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'talks', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'talks', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'talks', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'talks', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'talk', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'speak', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': '14'
}
ninth_mode_tags_to_remove = {
    'http://en.wikipedia.org/wiki/Judy_Woodruff': 'some', 'http://en.wikipedia.org/wiki/Condoleezza_Rice': 'that', 'http://en.wikipedia.org/wiki/Hillary_Rodham_Clinton': 'that', 'http://en.wikipedia.org/wiki/Carly_Fiorina': 'that', 'http://en.wikipedia.org/wiki/Martha_Stewart': 'that', 'http://en.wikipedia.org/wiki/Geraldine_Ferraro': 'that', 'http://en.wikipedia.org/wiki/Elizabeth_Smart': 'what'
}

# -------------------- #
# Configure Fast_Relax #
# -------------------- #
fast_relax.node_pick_policy = Sequential_Policy()
fast_relax.respect_initial_assignment_for_initializing_beliefs = True
fast_relax.has_converged = Fixed_Iter_Convergence(50)
# fast_relax.has_converged = Fixed_L2_Belief_Tolerance_Convergence(10, 1e-6)
fast_relax.verbose = True
