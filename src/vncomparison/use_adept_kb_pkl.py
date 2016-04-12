#!/usr/bin/env python
'''
| Filename    : use_adept_kb_pkl.py
| Description : Vertex Nomination Experiments on the Adept KB
| Author      : Pushpendre Rastogi
| Created     : Thu Mar 10 22:41:16 2016 (-0500)
| Last-Updated: Sat Mar 12 23:44:37 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 129
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
idx_to_name = dict((idx, entity_to_name[e])
                   for e, idx in entity_to_int_map.iteritems())
dv = data_dict.values()
edge_to_label_map = {}
for label, edges in data_dict.iteritems():
    for v1, v2 in edges:
        edge_to_label_map[(v1, v2)] = label
        edge_to_label_map[(v2, v1)] = label + '_inv'

all_nodes = set(rasengan.flatten(dv))
all_edges = reduce(lambda x, y: x + y, dv)
set_all_edges = set(tuple(e) for e in all_edges)


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
    n=220603, edges=list(set_all_edges), directed=False).simplify()
assert not any(g.is_multiple())

all_cmp = g.components()
cmp_bigger_than_1 = [e for e in all_cmp if len(e) > 1]
for e in cmp_bigger_than_1:
    if 22147 in e:
        cmp_22147 = e
        break

assert 78358 in cmp_22147
assert (len(all_cmp), sum(len(e) for e in all_cmp)) == (150338, 220603)
assert (len(cmp_bigger_than_1),
        sum(len(e) for e in cmp_bigger_than_1),
        max(len(e) for e in cmp_bigger_than_1)) == (5506, 75771, 63741)

tot = 0
cmpsize_to_cmp = defaultdict(list)
for e in list(all_cmp):
    cmpsize_to_cmp[len(e)].append(e)

cmpsize_to_cmp = dict(cmpsize_to_cmp)
if args.print_size_of_component_table:
    print 'Size-of-component, #components'
    for size in cmpsize_to_cmp:
        count = len(cmpsize_to_cmp)
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
for org_size in filter(lambda x: x >= args.min_org_size, sorted(size_to_org_dict.keys())[::5]):
    for p_removal in args.p_removal:
        m_prime = int(org_size * p_removal)
        assert m_prime != 0
        avg_success = 0.0
        for org in size_to_org_dict[org_size][:args.orgcount_inhibitor]:
            if org not in cmpsize_to_cmp[63741][0]:
                rasengan.warn(
                    "The organization:%d is not in the big component. CONTINUE!!" % org)
                continue

            employees = org_to_employees_dict[org]
            assert len(employees) == org_size
            success = 0.0
            print >> sys.stderr, '  Organization: ', idx_to_name[org]
            for trial_idx in range(args.k_trials):
                # Pick m_prime employees out of m employees
                employees_to_remove = random.sample(employees, m_prime)
                print >> sys.stderr, '    Employees Removed', ' '.join(
                    [idx_to_name[e] for e in employees_to_remove])
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
                    print '          ', idx_to_name[org],
                    try:
                        path = shortest_path(g, org, e)
                        print ' -> '.join([edge_to_label_map[pth] for pth in path]),
                    except ValueError:
                        print ' NO_PATH ',
                    print idx_to_name[e]
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
# import readline
# import code
# vars = globals().copy()
# vars.update(locals())
# code.InteractiveConsole(locals=vars).interact()
