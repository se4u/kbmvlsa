#!/usr/bin/env python
'''
| Filename    : evaluate_mad_on_sbm_graph.py
| Description : Evaluate perf of MAD algo for vertex nomination on SBM Graphs using JUNTO
| Author      : Pushpendre Rastogi
| Created     : Mon Feb 22 03:47:06 2016 (-0500)
| Last-Updated: Mon Feb 22 23:27:51 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 35
'''
import os
from compare_vn_strategy import loop_fnc
import rasengan
# Files to create:
JUNTO_DIR = os.getenv("JUNTO_DIR")
CFG_DIR = "%s/examples/simple/" % JUNTO_DIR
DATA_DIR = CFG_DIR + "data/"
graph_fn = DATA_DIR + "two_class_vn_graph"
seed_fn = DATA_DIR + "two_class_vn_seeds"
gold_labels_fn = DATA_DIR + "two_class_vn_gold_labels"
output_fn = DATA_DIR + "two_class_vn_label_prop_output"


class MAD(object):

    def __init__(self, edgelist):
        ''' An edgelist is a list of integer tuples that denote
        edges in a graph. The integers are vertex ids.
        '''
        self.edgelist = edgelist
        with open(graph_fn, "wb") as f:
            for e in edgelist:
                f.write('N%d\tN%d\t1\n' % (e))
        pass

    def write_train(self, label2id_map):
        # Write the file containing training data.
        with open(seed_fn, "wb") as f:
            for label, samples in label2id_map.items():
                for e in samples:
                    f.write('N%d\tL%d\t1\n' % (e, label))
        pass

    def write_test(self, label2id_map):
        # Write the file containing test data.
        with open(gold_labels_fn, "wb") as f:
            for label, samples in label2id_map.items():
                for e in samples:
                    f.write('N%d\tL%d\t1\n' % (e, label))
        pass

    def execute(self):
        retcode = os.system("cd %s; ./run.sh > tmp.log " % CFG_DIR)
        assert retcode == 0
        return retcode

    def parse_ratings(self):
        node_rating = {}
        for row in open(output_fn):
            row = row.strip().split('\t')
            node = int(row[0][1:])
            is_test = (row[-2] == 'true')
            tmp = row[3].split()
            assert len(tmp) % 2 == 0
            rating = dict(zip(tmp[::2], [float(e) for e in tmp[1::2]]))
            if is_test:
                node_rating[node] = rating
        return node_rating

    def parse(self, VC1):
        node_rating = self.parse_ratings()
        # score = rating['L1'] - rating['L0']
        nomination_list = sorted(
            node_rating.items(),
            key=lambda x: x[1]['L1'] - x[1]['L0'],
            reverse=True)
        relevance = [(1.0 if e in VC1 else 0.0)
                     for e, _
                     in nomination_list[:len(VC1)]]
        return (["%d" % sum(relevance)]
                + ["%.1f" % rasengan.rank_metrics.precision_at_k(relevance, k)
                   for k in [1, 5, 10, 50]])


def main(graph, VC0_S, VC1_S, block_sizes, **kwargs):
    ''' 1. Write graph, seed, and labels to text files.
    2. Call run.sh
    3. Parse the results in
    '''
    VC0 = range(block_sizes[0])
    VC1 = range(block_sizes[0], sum(block_sizes))
    edgelist = graph.get_edgelist()
    madobj = MAD(edgelist)
    madobj.write_train({0: VC0_S, 1: VC1_S})
    madobj.write_test({0: (set(VC0) - set(VC0_S)),
                       1: (set(VC1) - set(VC1_S))})
    madobj.execute()
    return madobj.parse(VC1)

if __name__ == '__main__':
    loop_fnc(main)
# Local Variables:
# eval: (progn (company-mode -1) (anaconda-mode -1) (eldoc-mode -1))
# eval: (progn (hs-minor-mode -1) (orgtbl-mode -1))
# End:
