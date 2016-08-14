#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
| Filename    : demonstrate_similarity_idea.py
| Description : Demonstrate the idea of finding common concepts between people.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 16:20:04 2016 (-0400)
| Last-Updated: Sat Aug 13 21:35:29 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 190

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
                # 2 Stage summation done for beleived extra numerical accuracy.
                # Since (sum small numbers) + big number is better than
                # (big number + small number) + small number + ...
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
                blf[problem[entity].index.get_loc(assignment[entity])] = 1
            blfs[entity] = blf
    else:
        for entity in problem:
            blf = numpy.ones(problem[entity].shape[0])
            blf = blf / blf.shape[0]
            blfs[entity] = blf
    return blfs


def fast_relax(problem, assignment):
    method_cfg = cfg.fast_relax
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
                entity, liloc(problem[entity], numpy.argmax(blfs[entity])).name)
    return post_process(blfs)


def variational_inference_update_belief(entity, problem, blfs, lambda_):
    complement_agg = numpy.zeros(problem[0].shape[1])
    e_prime_contrib = numpy.empty(problem[0].shape[1])
    for e_prime in problem:
        if e_prime != entity:
            e_prime_contrib[:] = 0.0
            for idx in range(problem[e_prime].shape[0]):
                e_prime_contrib += liloc(problem[e_prime], idx) * \
                    blfs[e_prime][idx]
        complement_agg += e_prime_contrib
    new_blfs = [numpy.dot(liloc(problem[entity], idx), complement_agg) / 2
                for idx
                in range(problem[entity].shape[0])]
    blfs[entity] = (lambda_ * blfs[entity]
                    + (1 - lambda_) * numpy.array(rasengan.exp_normalize(new_blfs)))
    assert len(blfs) == len(problem)
    return blfs


def variational_inference(problem, assignment):
    method_cfg = cfg.variational_inference
    blfs = get_blfs(problem, assignment, method_cfg)
    # Till convergence repeat
    while not method_cfg.has_converged(blfs):
        # Step 1: Choose Entity/Node/Variable
        entity_idx = method_cfg.node_pick_policy(len(problem))
        entity = problem.getkey(entity_idx)
        # Step 2: Optimize Entity Beliefs
        blfs = variational_inference_update_belief(
            entity, problem, blfs, method_cfg.lambda_)
        if method_cfg.verbose:
            print '%-25s best tag = %-10s' % (
                entity, liloc(problem[entity], numpy.argmax(blfs[entity])).name)
    return post_process(blfs)


def brute_force(problem, assignment):
    problem_mag = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
    for entity in problem.keys():
        problem_mag[entity] = [l2_norm_square(problem[entity].iloc[i])
                               for i in range(problem[entity].shape[0])]

    from rasengan import GrayCombinatorialCounter
    counter = GrayCombinatorialCounter(
        [problem[entity].shape[0] for entity in problem])
    total_vec = numpy.sum([problem[entity_idx].iloc[counter.state[entity_idx]]
                           for entity_idx in range(len(problem))], axis=0)
    total_mag = numpy.sum([problem_mag[entity_idx][counter.state[entity_idx]]
                           for entity_idx in range(len(problem))], axis=0)
    state2val = {}
    val = l2_norm_square(total_vec) - total_mag
    state2val[tuple(counter.state)] = val
    print ([problem[entity_idx].iloc[counter.state[entity_idx]].name
            for entity_idx in range(len(problem))], val)
    total_iter = 100.0 / reduce(lambda x, y: x * y, counter.lim)
    print total_iter
    for iter_idx, (entity_idx, old_val, new_val) in enumerate(counter):
        total_vec += (problem[entity_idx].iloc[new_val] -
                      problem[entity_idx].iloc[old_val])
        total_mag += (problem_mag[entity_idx][new_val]
                      - problem_mag[entity_idx][old_val])
        val = l2_norm_square(total_vec) - total_mag
        state2val[tuple(counter.state)] = val
        # print ([problem[entity_idx].iloc[counter.state[entity_idx]].name
        #         for entity_idx in range(len(problem))], val)
        if iter_idx % 10000 == 0:
            print iter_idx * total_iter


def dc_programming(problem, assignment):
    import cvxpy
    # Import the following for their side effects.
    from dccp.objective import convexify_obj
    from dccp.constraint import convexify_constr
    from dccp.linearize import linearize
    import dccp.problem
    N = [e.shape[0] for e in problem.itervalues()]
    X = [cvxpy.Variable(ni) for ni in N]
    constraints = [cvxpy.sum_entries(x) == 1 for x in X]
    constraints += [x >= 0 for x in X]
    if cfg.dc_programming.impose_integrality:
        constraints += [cvxpy.square(x) == x for x in X]
    objective_1 = sum([cvxpy.sum_squares(problem[entity].values.T * x)
                       for entity, x in zip(problem, X)])
    objective_2 = cvxpy.sum_squares(
        sum([(problem[entity].values.T * x) for entity, x in zip(problem, X)]))
    prob = cvxpy.Problem(
        cvxpy.Minimize(objective_1 - objective_2), constraints)
    result = prob.solve(method='dccp')
    blfs = rasengan.OrderedDict_Indexable_By_StringKey_Or_Index()
    for entity_idx in range(len(problem)):
        blfs[problem.getkey(entity_idx)] = X[entity_idx].value
    return post_process(blfs)


def optimize_assignment(problem, assignment, method='fast_relax'):
    assert method in [
        'brute_force', 'fast_relax', 'variational_inference', 'dc_programming']
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
        '--feat_file', default='data/random/details/89c0c894.American_women_writers', type=str)
    arg_parser.add_argument('--ctag', default=None, type=int)
    arg_parser.add_argument('--mode_count', default=5, type=int)
    arg_parser.add_argument('--method', default='fast_relax', type=str,
                            choices=['brute_force', 'fast_relax', 'annealed_gibbs',
                                     'maxproduct-bp', 'variational_inference', 'dc_programming'])
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
            print 'Initial chosen tags::', chosen_tags(problem, initial_assignment)
            initial_objective = dp_objective_efficient_impl(
                problem, initial_assignment)
            print 'initial_objective=', initial_objective
            assert numpy.isclose(dp_objective_naive_impl(problem, initial_assignment),
                                 initial_objective)
            final_assignment = optimize_assignment(
                problem, initial_assignment, method=args.method)
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
