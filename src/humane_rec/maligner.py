#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : maligner.py
| Description : Multi Aligner
| Author      : Pushpendre Rastogi
| Created     : Sun Sep 25 15:39:10 2016 (-0400)
| Last-Updated: Mon Sep 26 01:46:49 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 10
'''
import yaml
import rasengan
import cPickle as pkl
from pandas import DataFrame
import numpy
import demonstrate_similarity_idea_config as cfg
from collections import defaultdict
from pandas import DataFrame

def post_process(blfs):
    return dict((entity, numpy.argmax(blfs[entity]))
                for entity in blfs)

def get_blfs(problem, assignment, method_cfg):
    blfs = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
    # Initialize Node Beliefs
    method_cfg.has_converged.reset()
    if method_cfg.respect_initial_assignment_for_initializing_beliefs:
        for entity in problem:
            blf = numpy.zeros(problem[entity].shape[0])
            if isinstance(assignment[entity], int):
                blf[assignment[entity]] = 1
            else:
                # blf[problem[entity].index.get_loc(assignment[entity])] = 1
                raise NotImplementedError()
            blfs[entity] = blf
    else:
        for entity in problem:
            blf = numpy.ones(problem[entity].shape[0])
            blf = blf / blf.shape[0]
            blfs[entity] = blf
    return blfs


def fast_relax_optimize_belief(entity, problem, blfs):
    '''
    The optimization problem at this step is trivial.
    We have to optimize the beliefs for a particular entity, subject to the
    constraints that the beliefs must sum to one and must be positive.

    Define complement_aggregate to be equal to
    ∑_{/entity} ∑ belief[i] entity_vec[i]

    (|| ∑ belief[i] entity_vec[i] + complement_aggregate ||₂)² - (|| ∑ belief[i] entity_vec[i] ||₂)²
    The solution to this problem is simply to choose the entity vector that best matches
    the complement_aggregate.

    These moves are similar to the way that k-means works.
    '''
    complement_agg = numpy.zeros(problem[0].shape[1])
    e_prime_contrib = numpy.empty(problem[0].shape[1])
    for e_prime in problem:
        if e_prime != entity:
            e_prime_contrib[:] = 0.0
            for idx in range(problem[e_prime].shape[0]):
                # 2 Stage summation done for beleived extra numerical accuracy.
                # Since (sum small numbers) + big number is better than
                # (big number + small number) + small number + ...
                e_prime_contrib += problem[e_prime].iloc[idx] * blfs[e_prime][idx]
        complement_agg += e_prime_contrib
    best_idx = numpy.argmax([
        numpy.dot(problem[entity].iloc[idx], complement_agg)
        for idx
        in range(problem[entity].shape[0])])
    blfs[entity][:] = 0
    blfs[entity][best_idx] = 1
    return blfs

def fast_relax(problem, assignment, method_cfg):
    assert isinstance(problem, rasengan.OrderedDict_Indexable_By_StringKey_Or_Index)
    blfs = get_blfs(problem, assignment, method_cfg)
    # Till Convergence, repeat
    while not method_cfg.has_converged(blfs):
        # Step 1: Choose Entity/Node/Variable
        entity_idx = method_cfg.node_pick_policy(len(problem))
        entity = problem.getkey(entity_idx)
        # Step 2: Optimize Entity Beliefs
        blfs = fast_relax_optimize_belief(entity, problem, blfs)
        if method_cfg.verbose:
            print '%-25s best tag = %-10s' % (
                entity, problem[entity].iloc[numpy.argmax(blfs[entity])].name)
    assignment = post_process(blfs)
    topic = {}
    for k, v in assignment.iteritems():
        topic[k] = problem[k].index[v]
    return topic
