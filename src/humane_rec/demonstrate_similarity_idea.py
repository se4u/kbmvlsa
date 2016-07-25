#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : demonstrate_similarity_idea.py
| Description : Demonstrate the idea of finding common concepts between people.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 16:20:04 2016 (-0400)
| Last-Updated: Mon Jul 25 01:33:21 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 28

Data Structures
---------------
problem: An OrderedDict of Pandas DataFrames with named rows.
assignment: A map from problem keys to an int that references a row in the problem[key] DataFrame.
'''
import yaml
import rasengan
import cPickle as pkl
from pandas import DataFrame
import numpy
import demonstrate_similarity_idea_config as cfg


def chosen_tags(problem, assignment):
    return ', '.join([
        '%s: %s' % (entity, problem[entity].iloc[assignment[entity]].name)
        for entity in assignment])


def dp_objective_naive_impl(problem, assignment):
    entities = problem.keys()
    objective = 0.0
    for a in entities:
        for b in entities:
            if a != b:
                objective += numpy.dot(problem[a].iloc[assignment[a]].values,
                                       problem[b].iloc[assignment[b]].values)
    return objective / 2


def l2_norm_square(v):
    return sum(v * v)


def dp_objective_efficient_impl(problem, assignment):
    aggregate_vec = sum(problem[a].iloc[assignment[a]].values
                        for a in problem)
    aggregate_exclusion = sum(l2_norm_square(problem[a].iloc[assignment[a]].values)
                              for a in problem)
    return (l2_norm_square(aggregate_vec) - aggregate_exclusion) / 2


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
    import pdb
    pdb.set_trace()
    complement_agg = numpy.zeros(problem[0].shape[1])
    e_prime_contrib = numpy.empty(problem[0].shape[1])
    for e_prime in problem:
        if e_prime != entity:
            e_prime_contrib[:] = 0.0
            for idx in range(problem[e_prime].shape[0]):
                e_prime_contrib += problem[e_prime].iloc[idx] * \
                    blfs[e_prime][idx]
        complement_agg += e_prime_contrib
    best_idx = numpy.argmax([
        numpy.dot(problem[entity].iloc[idx], complement_agg)
        for idx
        in range(problem[entity].shape[0])])
    blfs[entity][:] = 0
    blfs[entity][best_idx] = 1
    return blfs


def fast_relax(problem, assignment):
    import pdb
    pdb.set_trace()
    blfs = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
    # Initialize Node Beliefs
    if cfg.fast_relax.respect_initial_assignment_for_initializing_beliefs:
        for entity in problem:
            blf = numpy.zeros(problem[entity].shape[0])
            blf[assignment[entity]] = 1
            blfs[entity] = blf
    else:
        for entity in problem:
            blf = numpy.ones(problem[entity].shape[0])
            blf = blf / blf.shape[0]
            blfs[entity] = blf

    # Till Convergence, repeat
    while not cfg.fast_relax.has_converged(blfs):
        # Step 1: Choose Entity/Node/Variable
        entity_idx = cfg.fast_relax.node_pick_policy(len(problem))
        entity = problem.getkey(entity_idx)
        # Step 2: Optimize Entity Beliefs
        blfs = fast_relax_optimize_belief(entity, problem, blfs)

    return


def optimize_assignment(problem, assignment, method='fast_relax'):
    assert method in ['fast_relax', 'annealed_gibbs', 'maxproduct-bp']
    method = eval(method)
    return method(problem, assignment)


def main():
    with rasengan.debug_support():
        yaml_data = yaml.load(open('data/women_writer_manual_clues.yaml'))
        entity_tags = dict([(a, set(rasengan.flatten(b[1::2])))
                            for a, b in yaml_data.items()])
        total_tags = set(
            rasengan.flatten([(rasengan.flatten(b[1::2])) for b in yaml_data.values()]))
        embeddings = pkl.load(open('data/demonstrate_similarity_idea.emb.pkl'))
        assert all(e in embeddings for e in total_tags)
        print ('For each of these people our goal is to select one word.'
               ' That word should be as similar to other words picked for other'
               ' entities as possible')

        problem = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
        for (a, b) in entity_tags.items():
            b = list(b)
            print '%-25s' % a, '|||', ', '.join(b)
            problem[a] = DataFrame(
                data=numpy.concatenate([embeddings[e][None, :]
                                        for e in b], axis=0),
                index=b)

        people_without_relevant_tags = [
            'Geraldine_Ferraro', 'Elizabeth_Smart', 'Judy_Woodruff']

        initial_assignment = {
            'Condoleezza_Rice': 0,
            'Carly_Fiorina': 1,
            'Geraldine_Ferraro': 2,
            'Judy_Woodruff': 3,
            'Elizabeth_Smart': 4,
            'Martha_Stewart': 5,
            'Hillary_Rodham_Clinton': 6}

        print 'Initial chosen tags::', chosen_tags(problem, initial_assignment)
        initial_objective = dp_objective_efficient_impl(
            problem, initial_assignment)
        assert numpy.isclose(dp_objective_naive_impl(problem, initial_assignment),
                             initial_objective)
        final_assignment = optimize_assignment(problem, initial_assignment)
        final_objective = dp_objective_efficient_impl(
            problem, final_assignment)
        print 'initial_objective=', initial_objective,\
            'final_objective=', final_objective,\
            'Final chosen tags=', chosen_tags(problem, final_assignment)
    return

main()
