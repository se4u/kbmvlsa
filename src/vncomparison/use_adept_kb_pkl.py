#!/usr/bin/env python
'''
| Filename    : use_adept_kb_pkl.py
| Description : Vertex Nomination Experiments on the Adept KB
| Author      : Pushpendre Rastogi
| Created     : Thu Mar 10 22:41:16 2016 (-0500)
| Last-Updated: Mon Mar 21 11:21:22 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 201
'''
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
arg_parser.add_argument('--p_removal', type=int, nargs='*', default=[0.25, 0.5],
                        help='Default={(0.25, 0.5)}')
arg_parser.add_argument(
    '--min_org_size', default=6, type=int, help='Default={6}')
arg_parser.add_argument('--k_trials', default=5, type=int, help='Default={5}')
arg_parser.add_argument('--data_pkl', default='../../res/adept.pkl', type=str)
arg_parser.add_argument('--entity_to_name_pkl',
                        default='../../res/entity_to_string.pkl', type=str)
arg_parser.add_argument(
    '--rw_walk_num', default=3, type=int, help='Default={5}')
arg_parser.add_argument(
    '--rw_max_step', default=10, type=int, help='Default={10}')
arg_parser.add_argument('--print_size_of_component_table', default=0, type=int,
                        help='Default={0}')
arg_parser.add_argument(
    '--orgcount_inhibitor', default=10, type=int, help='Default={10}')
args = arg_parser.parse_args()
import random
import numpy as np
import sys
random.seed(args.seed)
np.random.seed(args.seed)
import cPickle as pkl
import rasengan
import igraph
from collections import defaultdict, Counter
import contextlib
from scipy.sparse import lil_matrix
from rescal import rescal_als
from compare_vn_strategy import predict_rescal_als


def histogram(iterable, hash_fnc, descending=True):
    hist = defaultdict(int)
    for e in list(iterable):
        hist[hash_fnc(e)] += 1
    return sorted(hist.items(), key=lambda x: x[1], reverse=descending)


def print_total_nodes_and_edges(entity_to_int_map, data_dict):
    print 'Total Nodes=', len(entity_to_int_map)
    total = 0
    for idx, k in enumerate(data_dict):
        l = len(data_dict[k])
        print '%-3d' % idx, '%-60s' % k, l
        total += l
    print 'Total Edges=', total
    return

data = pkl.load(open(args.data_pkl))
entity_to_name = pkl.load(open(args.entity_to_name_pkl))
entity_to_int_map = data['entity_to_int_map']
data_dict = data['data_dict']
# rasengan.warn('I am deleting Role_person_to_role')
# del data_dict['Role_person_to_role']
# rasengan.warn('I am deleting Resident_location_to_person')
# del data_dict['Resident_location_to_person']

idx_to_name = dict((idx, entity_to_name[e])
                   for e, idx in entity_to_int_map.iteritems())
int_to_entity_map = dict((a, b) for (b, a) in entity_to_int_map.iteritems())
dv = data_dict.values()


edge_to_label_map = {}
for label, edges in data_dict.iteritems():
    for v1, v2 in edges:
        edge_to_label_map[(v1, v2)] = label
        edge_to_label_map[(v2, v1)] = label + '_inv'

all_nodes = set(rasengan.flatten(dv))
all_edges = reduce(lambda x, y: x + y, dv)
set_all_edges = set(tuple(e) for e in all_edges)
# print '\n'.join([str(e)
#                  for e
#                  in sorted(list(set([(idx_to_name[e[1]],
#                                       g.degree(e[1])) for e in
#                                      data_dict['Role_person_to_role']
#                                      if g.degree(e[1]) == 2])),
#                            key=lambda x: x[1], reverse=True)])


def shortest_path(g, v1, v2):
    d = {}
    v = None
    pv = None
    for v, dist, pv in g.bfsiter(v1, advanced=True):
        v = v.index
        if pv is not None:
            pv = pv.index
        d[v] = pv
        if v == v2:
            break
    if v != v2:
        raise ValueError("No path from %d to %d" % (v1, v2))
    path = [v]
    for _ in range(dist):
        path.insert(0, pv)
        pv = d[pv]

    pth = []
    for idx in range(1, len(path)):
        pth.append((path[idx - 1], path[idx]))
    return pth

g = igraph.Graph(
    n=220603, edges=list(set_all_edges), directed=False)

g = g.simplify()
p2l = defaultdict(list)
p2e = defaultdict(list)
p2r = defaultdict(list)
p2o = defaultdict(list)
for a, b in data_dict['Resident_location_to_person']:
    p2l[b].append(a)
for a, b in data_dict['Origin_affiliatedEntity_to_person']:
    p2e[b].append(a)
for a, b in data_dict['Role_person_to_role']:
    p2r[a].append(b)
for a, b in data_dict['EmploymentMembership_organization_to_employeeMember']:
    p2o[b].append(a)
p_list = set(p2l.keys() + p2e.keys() + p2r.keys() + p2o.keys())
pler = dict([(p, set([(l, e, r) for l in p2l[p] for e in p2e[p] for r in p2r[p]]))
             for p in set(p2l.keys() + p2e.keys() + p2r.keys())])
# p1p2 = [(p1, p2) for p1 in pler for p2 in pler
#         if p1 != p2 and len(pler[p1].intersection(pler[p2])) > 0]

assert not any(g.is_multiple())

all_cmp = g.components()
cmp_bigger_than_1 = [e for e in all_cmp if len(e) > 1]
for e in cmp_bigger_than_1:
    if 22147 in e:
        cmp_22147 = e
        break
cmp_22147_mask = [1 if e in p_list else 0 for e in cmp_22147]
# assert 78358 in cmp_22147
# assert (len(all_cmp), sum(len(e) for e in all_cmp)) == (150338, 220603)
# assert (len(cmp_bigger_than_1),
#         sum(len(e) for e in cmp_bigger_than_1),
#         max(len(e) for e in cmp_bigger_than_1)) == (5506, 75771, 63741)

tot = 0
cmpsize_to_cmp = defaultdict(list)
for e in list(all_cmp):
    cmpsize_to_cmp[len(e)].append(e)

cmpsize_to_cmp = dict(cmpsize_to_cmp)
if args.print_size_of_component_table:
    print 'Size-of-component, #components'
    for size in cmpsize_to_cmp:
        count = len(cmpsize_to_cmp[size])
        sc = size * count
        tot += sc
        print '%-8d%-8d%-8d%-8d' % (size, count, sc, tot)


# ------------------------------------------------------- #
# Q. Which relations created the two clusters of size 10? #
# ------------------------------------------------------- #
# print [[(_, idx_to_name[_]) for _ in e]
#        for e in all_cmp if len(e) == 10]
# These two clusters are:
# 1. http://fantasywta.forums-actifs.net/t1708p45-german-survivor-winners-s-lisicki-t-haas
# 2. http://www.christianforums.com/threads/best-commentaries.2658307/
# Note that "Robert Gundry Morna D. Hooker" has two types.
# grep "Robert Gundry Morna D. Hooker" bbn_2016-02-23_13-09-09-base.nq
# grep cf69d255-88ed-4fe7-b726-d0e1f0f940d1 bbn_2016-02-23_13-09-09-ont-types.nq
# # core#Person
# grep c6f8f437-3be6-4fca-b77f-52e6e2172b0f bbn_2016-02-23_13-09-09-ont-types.nq
# # core#Title
# -------------------------------------------------------- #

# Role_person_to_role                                     42491
# EmploymentMembership_organization_to_employeeMember     36631
# InvestorShareholder_organization_to_investorShareholder 530
# Origin_affiliatedEntity_to_person                       2764
# Die_victim_to_agent                                     0
# Membership_organization_to_member                       369
# OrgHeadquarter_location_to_organization                 7242
# Resident_location_to_person                             16288
# OrganizationWebsite_organization_to_url                 200
# ChargeIndict_defendant_to_crime                         387
# Founder_organization_to_founder                         1281
# Leadership_leader_to_affiliatedEntity                   9600
# StudentAlum_organization_to_studentAlumni               1306
# ParentChildRelationship_parent_to_child                 1774
org_to_employees_dict = defaultdict(list)
for o, e in data_dict['EmploymentMembership_organization_to_employeeMember']:
    org_to_employees_dict[o].append(e)

size_to_org_dict = defaultdict(list)
for o, el in org_to_employees_dict.iteritems():
    size_to_org_dict[len(el)].append(o)

# print 'Degree distribution', sorted(Counter(g.degree()).items(), key=lambda x: x[0])
# print [idx_to_name[e] for e in range(g.vcount()) if g.degree(e) > 1000]

sp_list = []
print 'Org Size, Member Removal Factor, Success Upper Bound'
for org_size in filter(lambda x: x >= args.min_org_size,
                       sorted(size_to_org_dict.keys(), reverse=True)[::5]):
    for p_removal in args.p_removal:
        m_prime = int(org_size * p_removal)
        assert m_prime != 0
        avg_success = 0.0
        for org in size_to_org_dict[org_size][:args.orgcount_inhibitor]:
            employees = org_to_employees_dict[org]
            assert len(employees) == org_size
            success = 0.0
            print >> sys.stderr, '  Organization: ', idx_to_name[org]
            # print int_to_entity_map[org]
            for trial_idx in range(args.k_trials):
                # Pick m_prime employees out of m employees
                employees_to_remove = random.sample(employees, m_prime)
                print >> sys.stderr, '    Employees Removed', ' '.join(
                    [idx_to_name[e] for e in employees_to_remove])
                print [idx_to_name[e]] + [idx_to_name[_]
                                          for _ in g.neighbors(e)]
                print >> sys.stderr, '    Employees Kept', ' '.join(
                    [idx_to_name[e] for e in employees
                     if e not in employees_to_remove])
                print >> sys.stderr, ('        Shortest path b/w org and employee BEFORE deletion: ' +
                                      str(g.shortest_paths(org, employees_to_remove)))
                # Delete Edges
                g.delete_edges([(org, employee)
                                for employee
                                in employees_to_remove])
                gsp = rasengan.flatten(
                    g.shortest_paths(org, employees_to_remove))
                assert 1 not in gsp
                sp_list.extend(gsp)
                print >> sys.stderr, ('        Shortest path b/w org and employee AFTER deletion: ' +
                                      str(gsp))
                for e in employees_to_remove:
                    for e in employees_to_remove:
                        assert cmp_22147_mask[cmp_22147.index(e)]
                    print '          ', idx_to_name[org],
                    try:
                        path = shortest_path(g, org, e)
                        print ' -> '.join([edge_to_label_map[pth] for pth in path]), \
                            ' '.join(['->'.join((idx_to_name[a], idx_to_name[b]))
                                      for a, b in shortest_path(g, org, e)]),
                    except ValueError:
                        print ' NO_PATH ',
                    print idx_to_name[e]

                # This is the induced subgraph with the deleted edges.
                # We can do RESCAL on the dependency matrix of this induced
                # subgraph.
                my_subgraph = g.induced_subgraph(cmp_22147)
                my_subgraph_adj = lil_matrix((my_subgraph.vcount(),
                                              my_subgraph.vcount()),
                                             dtype='uint8')
                for eel in my_subgraph.get_edgelist():
                    my_subgraph_adj[eel[0], eel[1]] = 1

                T = [lil_matrix(my_subgraph_adj)]
                A, R, _, _, _ = rescal_als(
                    T, 10, init='nvecs', conv=1e-3, lambda_A=1, lambda_R=1)
                idx_of_org_in_cmp_22147 = cmp_22147.index(org)
                als_prediction = np.dot(
                    np.dot(A[idx_of_org_in_cmp_22147], R[0]), A.T)
                # Now based on this ranking find out what the rank of
                # the true employees would be.
                als_pred_of_employees_removed = [als_prediction[cmp_22147.index(e)]
                                                 for e in employees_to_remove]

                sorted_als_pred = sorted(
                    filter(
                        lambda x: cmp_22147_mask[x[0]], enumerate(als_prediction)),
                    reverse=True,
                    key=lambda x: x[1])
                sorted_als_pred_idx = [e[0] for e in sorted_als_pred]
                sorted_als_pred_val = [e[1] for e in sorted_als_pred]
                rank_of_removed_employees = [sorted_als_pred_val.index(e)
                                             for e in als_pred_of_employees_removed]
                # I need to find out which of the vertices ranked above me
                # me should I filter out?
                print 'Rank of Removed Employees', rank_of_removed_employees
                # Do a random walk.
                # Now I want to do a random walk on this graph.
                vertex_hits = Counter(
                    rasengan.flatten(
                        g.random_walk(org, args.rw_max_step)
                        for walk_idx in range(args.rw_walk_num)))
                print >> sys.stderr, '            Most common hit', ' '.join(
                    [idx_to_name[e[0]] for e in vertex_hits.most_common(5)])
                success += any(e in vertex_hits for e in employees_to_remove)
                # Restore Graph #
                g.add_edges([(org, employee)
                             for employee
                             in employees_to_remove])

            success /= args.k_trials
            avg_success += success
            pass
        avg_success /= len(size_to_org_dict[org_size]
                           [:args.orgcount_inhibitor])
        print '%-2d %.2f %.2f ' % (org_size, p_removal, avg_success), 'ORG Count:', \
            len(size_to_org_dict[org_size][:args.orgcount_inhibitor])

print Counter(sp_list)
#  Local Variables:
#  eval: (anaconda-mode -1)
#  End:
