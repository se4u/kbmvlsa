#!/usr/bin/env python
'''
| Filename    : evaluate_mad_on_sbm_graph.py
| Description : Evaluate perf of MAD algo for vertex nomination on SBM Graphs using JUNTO
| Author      : Pushpendre Rastogi
| Created     : Mon Feb 22 03:47:06 2016 (-0500)
| Last-Updated: Mon Feb 22 05:57:05 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 29
'''
import os
from compare_vn_strategy import loop_fnc
from rasengan import rank_metrics
# Files to create:
JUNTO_DIR = os.getenv("JUNTO_DIR")
CFG_DIR = "%s/examples/simple/" % JUNTO_DIR
DATA_DIR = CFG_DIR + "data/"
graph_fn = DATA_DIR + "two_class_vn_graph"
seed_fn = DATA_DIR + "two_class_vn_seeds"
gold_labels_fn = DATA_DIR + "two_class_vn_gold_labels"
output_fn = DATA_DIR + "two_class_vn_label_prop_output"


def parse_ratings():
    node_rating = {}
    for row in open(output_fn):
        row = row.strip().split('\t')
        node = int(row[0][1:])
        is_test = (row[-2] == 'true')
        tmp = row[3].split()
        assert len(tmp) % 2 == 0
        rating = dict(zip(tmp[::2], [float(e) for e in tmp[1::2]]))
        score = rating['L1'] - rating['L0']
        if is_test:
            node_rating[node] = score
    return node_rating


def parse(VC1):
    node_rating = parse_ratings()
    nomination_list = sorted(
        node_rating.items(), key=lambda x: x[1], reverse=True)
    relevance = [(1.0 if e in VC1 else 0.0)
                 for e, _
                 in nomination_list[:len(VC1)]]
    return ["%d" % sum(relevance)] + ["%.1f" % rank_metrics.precision_at_k(relevance, k)
                                      for k in [1, 5, 10, 50]]


def main(graph, VC0_S, VC1_S, block_sizes, **kwargs):
    ''' 1. Write graph, seed, and labels to text files.
    2. Call run.sh
    3. Parse the results in
    '''
    VC0 = range(block_sizes[0])
    VC1 = range(block_sizes[0], sum(block_sizes))
    edgelist = graph.get_edgelist()
    with open(graph_fn, "wb") as f:
        for e in edgelist:
            f.write('N%d\tN%d\t1\n' % (e))

    with open(seed_fn, "wb") as f:
        for e in VC0_S:
            f.write('N%d\tL0\t1\n' % e)
        for e in VC1_S:
            f.write('N%d\tL1\t1\n' % e)

    with open(gold_labels_fn, "wb") as f:
        for e in (set(VC0) - set(VC0_S)):
            f.write('N%d\tL0\t1\n' % e)
        for e in (set(VC1) - set(VC1_S)):
            f.write('N%d\tL1\t1\n' % e)

    retcode = os.system("cd %s; ./run.sh " % CFG_DIR)
    assert retcode == 0
    return parse(VC1)

if __name__ == '__main__':
    loop_fnc(main)
# Local Variables:
# eval: (progn (company-mode -1) (anaconda-mode -1) (eldoc-mode -1))
# eval: (progn (hs-minor-mode -1) (orgtbl-mode -1))
# End:
