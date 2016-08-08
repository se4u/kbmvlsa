#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : demonstrate_similarity_idea.py
| Description : Demonstrate the idea of finding common concepts between people.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 16:20:04 2016 (-0400)
| Last-Updated: Mon Aug  8 16:18:35 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 118

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
from collections import defaultdict
# FUNCTION_WORDS = set(get_function_words())


def liloc(df, k):
    return (df.iloc[k]
            if isinstance(k, int)
            else df.loc[k])


def chosen_tags(problem, assignment):
    builder = []
    for entity in assignment:
        builder.append(
            '%s: %s' % (entity, liloc(problem[entity], assignment[entity]).name))
    return ', '.join(builder)


def dp_objective_naive_impl(problem, assignment):
    entities = problem.keys()
    objective = 0.0
    for a in entities:
        for b in entities:
            if a != b:
                objective += numpy.dot(liloc(problem[a], assignment[a]).values,
                                       liloc(problem[b], assignment[b]).values)
    return objective / 2


def l2_norm_square(v):
    return sum(v * v)


def dp_objective_efficient_impl(problem, assignment):
    aggregate_vec = sum(liloc(problem[a], assignment[a]).values
                        for a in problem)
    aggregate_exclusion = sum(l2_norm_square(liloc(problem[a], assignment[a]).values)
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
    complement_agg = numpy.zeros(problem[0].shape[1])
    e_prime_contrib = numpy.empty(problem[0].shape[1])
    for e_prime in problem:
        if e_prime != entity:
            e_prime_contrib[:] = 0.0
            for idx in range(problem[e_prime].shape[0]):
                e_prime_contrib += liloc(problem[e_prime], idx) * \
                    blfs[e_prime][idx]
        complement_agg += e_prime_contrib
    best_idx = numpy.argmax([
        numpy.dot(liloc(problem[entity], idx), complement_agg)
        for idx
        in range(problem[entity].shape[0])])
    blfs[entity][:] = 0
    blfs[entity][best_idx] = 1
    return blfs


def fast_relax_post_process(blfs):
    return dict((entity, numpy.argmax(blfs[entity]))
                for entity in blfs)


def fast_relax(problem, assignment):
    blfs = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
    # Initialize Node Beliefs
    cfg.fast_relax.has_converged.reset()
    if cfg.fast_relax.respect_initial_assignment_for_initializing_beliefs:
        for entity in problem:
            blf = numpy.zeros(problem[entity].shape[0])
            if isinstance(assignment[entity], int):
                blf[assignment[entity]] = 1
            else:
                blf[problem[entity].index.get_loc(assignment[entity])] = 1
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
        if cfg.fast_relax.verbose:
            print '%-25s best tag = %-10s' % (
                entity, liloc(problem[entity], numpy.argmax(blfs[entity])).name)

    return fast_relax_post_process(blfs)


def optimize_assignment(problem, assignment, method='fast_relax'):
    assert method in ['fast_relax', 'annealed_gibbs', 'maxproduct-bp']
    method = eval(method)
    return method(problem, assignment)


def tolerant_remove(l, v):
    try:
        l.remove(v)
    except ValueError:
        pass


def scale_to_unit(v):
    assert v.ndim == 1
    n = numpy.linalg.norm(v)
    return (v if n == 0 else v / n)


def main():
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--emb_pkl_fn', default='data/demonstrate_similarity_idea.emb.pkl', type=str)
    arg_parser.add_argument(
        '--ent_file', default='data/category_to_entities/American_women_writers', type=str)
    arg_parser.add_argument(
        '--feat_file', default='data/entity_descriptors_procoref~1.psv', type=str)
    arg_parser.add_argument('--ctag', default=None, type=int)
    arg_parser.add_argument('--mode_count', default=5, type=int)
    args = arg_parser.parse_args()
    import random
    random.seed(args.seed)
    numpy.random.seed(args.seed)
    cfg.mode_count = args.mode_count
    tags_to_remove = defaultdict(list)
    with rasengan.tictoc('Loading pkl'):
        embeddings = pkl.load(open(args.emb_pkl_fn))
        if cfg.introduce_NULL_embedding:
            embeddings[cfg.NULL_KEY] = numpy.zeros(
                next(embeddings.itervalues()).shape)
    with rasengan.debug_support():
        for mode_idx in range(cfg.mode_count):
            print 'mode_idx=', mode_idx
            if cfg.use_big_tag_set:
                entity_tags = {}
                entities = []
                for row in open(args.feat_file):
                    _e, _tags = [e.strip() for e in row.strip().split('|||')]
                    entities.append(_e)
                    entity_tags[_e] = set(
                        [t.lower()
                         for t in (e.strip().split(':')[0]
                                   for e in _tags.split())
                         if t.lower() in embeddings])
                total_tags = set(
                    rasengan.flatten([list(e) for e in entity_tags.values()]))
            else:
                yaml_data = yaml.load(
                    open('data/women_writer_manual_clues.yaml'))
                entity_tags = dict([(a, set(rasengan.flatten(b[1::2])))
                                    for a, b in yaml_data.items()])
                total_tags = set(
                    rasengan.flatten([(rasengan.flatten(b[1::2])) for b in yaml_data.values()]))

            assert all(e in embeddings for e in total_tags)
            print ('For each of these people our goal is to select one word.'
                   ' That word should be as similar to other words picked for other'
                   ' entities as possible')

            problem = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
            for (a, b) in entity_tags.items():
                b = list(b)
                print 'Entity: ', a, 'tags to remove: ', tags_to_remove[a]
                for ttr in tags_to_remove[a]:
                    tolerant_remove(b, ttr)
                if cfg.introduce_NULL_embedding and cfg.NULL_KEY not in b:
                    b.append(cfg.NULL_KEY)
                # print '%-25s' % a, '|||', ', '.join(b)
                problem[a] = DataFrame(
                    data=numpy.concatenate(
                        [(scale_to_unit(embeddings[e])
                          if cfg.scale_to_unit
                          else embeddings[e])[None, :]
                         for e in b], axis=0),
                    index=b)
            if cfg.use_big_tag_set:
                if args.ctag is None:
                    initial_assignment = dict((__a, 0)
                                              for __b, __a
                                              in enumerate(entities))
                else:
                    ctag = 'war'.split()[args.ctag]
                    initial_assignment = dict((__e,
                                               (cfg.NULL_KEY
                                                if ctag not in entity_tags[__e]
                                                else ctag))
                                              for __e in entities)
            else:
                initial_assignment = {
                    'Condoleezza_Rice': 0,
                    'Carly_Fiorina': 1,
                    'Geraldine_Ferraro': 2,
                    'Judy_Woodruff': 3,
                    'Elizabeth_Smart': 4,
                    'Martha_Stewart': 5,
                    'Hillary_Rodham_Clinton': 6}
                initial_assignment = {
                    'Condoleezza_Rice': 0,
                    'Carly_Fiorina': 0,
                    'Geraldine_Ferraro': 0,
                    'Judy_Woodruff': 0,
                    'Elizabeth_Smart': 0,
                    'Martha_Stewart': 0,
                    'Hillary_Rodham_Clinton': 0}

            print 'Initial chosen tags::', chosen_tags(problem, initial_assignment)
            initial_objective = dp_objective_efficient_impl(
                problem, initial_assignment)
            print 'initial_objective=', initial_objective
            assert numpy.isclose(dp_objective_naive_impl(problem, initial_assignment),
                                 initial_objective)
            exit(1)
            final_assignment = optimize_assignment(problem, initial_assignment)
            final_objective = dp_objective_efficient_impl(
                problem, final_assignment)
            for (fa_entity, fa_tag_idx) in final_assignment.iteritems():
                tags_to_remove[fa_entity].append(
                    liloc(problem[fa_entity], fa_tag_idx).name)
            print 'mode_idx=', mode_idx,
            print 'initial_objective=', initial_objective,
            print 'final_objective=', final_objective,
            print 'Final chosen tags=', chosen_tags(problem, final_assignment)
    return

if __name__ == '__main__':
    main()
