#!/usr/bin/env python
'''
| Filename    : wikimic_identify_governors.pkl.py
| Description : Identify Governors according to the dependency relations.
| Author      : Pushpendre Rastogi
| Created     : Thu Aug  4 03:06:45 2016 (-0400)
| Last-Updated: Fri Aug  5 13:47:48 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 16
Each mention contains:
e_sent_idx /in e_sent/, (e_sent, e_parse) /in sentences/, lot, referent
'''

import rasengan
from rasengan import sPickle
import itertools
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--in_fn', type=str)
arg_parser.add_argument('--out_fn', type=str)
args = arg_parser.parse_args()


def unwrap_mention(m_list):
    for m in m_list:
        yield (m["s"], m["p"], m["r"])

with open(args.in_fn) as in_f, rasengan.open_wmdoe(args.out_fn) as out_f:
    with rasengan.debug_support():
        for entity, mentions in sPickle.s_load(in_f):
            out_mentions = []
            for mention in mentions:
                for m_idx, (sent, parse, referents) in enumerate(
                        unwrap_mention(mention["sentences"])):
                    # Initialize the descriptors.
                    ETS = referents
                    B = {}
                    D = {}
                    CONVERGED = False
                    (ID, W, Tc, Tf, P, R) = rasengan.reshape_conll(
                        [_.strip().split('\t') for _ in parse])
                    # NOTE: This pattern of growing a set to convergence by
                    # applying rules should be repeatable. It would probably
                    # need standardization of what we are growing.
                    # Grow descriptors till convergence.
                    while not CONVERGED:
                        OLD_LEN_BD = len(B) + len(D)
                        for (i, w, tc, tf, p, r) in itertools.izip(
                                ID, W, Tc, Tf, P, R):
                            if ((p in ETS and r == 'appos')
                                    or (p in D and r in ['acomp', 'nn'])
                                    or (P[p] in D and r in ['pobj', 'pcomp'])
                                    or (p in B and r in ['pobj', 'dobj'])
                                    or (P[p] in B and R[p] in ['pobj', 'dobj']) and r == 'conj'):
                                D[i] = True
                            if ((i in ETS and r in ['nsubj', 'nsubjpass'])
                                    or (i in ETS and r in ['poss', 'advmod'])):
                                D[p] = True
                            if (Tc[p] == 'VERB' and r == 'dobj' and p in D):
                                B[p] = True
                        NEW_LEN_BD = len(B) + len(D)
                        CONVERGED = (NEW_LEN_BD == OLD_LEN_BD)
                        pass
                    mention["sentences"][m_idx]["d"] = D
                    print 'Selected Words:', [W[_] for _ in D], 'from', W, 'for', entity
                    import pdb
                    pdb.set_trace()
                    out_mentions.append(mention)
                    pass
                pass
            sPickle.s_dump_elt((entity, out_mentions), out_f)
