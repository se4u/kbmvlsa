#!/usr/bin/env python
'''
| Filename    : wikimic_identify_governors.pkl.py
| Description : Identify Governors according to the dependency relations.
| Author      : Pushpendre Rastogi
| Created     : Thu Aug  4 03:06:45 2016 (-0400)
| Last-Updated: Thu Aug  4 11:47:38 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 2
Each mention contains:
e_sent_idx /in e_sent/, (e_sent, e_parse) /in sentences/, lot, referent
'''

from rasengan import pklflow_ctx


def unwrap_mention(m_list):
    for m in m_list:
        yield (m["s"], m["p"], m["r"])

with pklflow_ctx(in_fn="data/wikimic_identify_governors.pkl",
                 out_fn="data/wikimic_create_entity_token_set.pkl") as ns:
    out_data = {}
    for entity, mentions in ns.data.iteritems():
        out_data[entity] = []
        for mention in mentions:
            out_mention = mention
            for m_idx, (sent, parse, referents) in enumerate(mention["sentences"]):
                # Initialize the descriptors.
                ETS = referents
                B = {}
                D = {}
                CONVERGED = False
                (ID, W, Tc, Tf, P, R) = parse
                # NOTE: This pattern of growing a set to convergence by
                # applying rules should be repeatable. It would probably
                # need standardization of what we are growing.
                # Grow descriptors till convergence.
                while not CONVERGED:
                    OLD_LEN_BD = len(B) + len(D)
                    for (i, w, tc, tf, p, r) in zip(*parse):
                        if ((p in ETS and r == 'appos')
                                or (p in D and r in ['acomp', 'nn'])
                                or (P[p] in D and r in ['pobj', 'pcomp'])
                                or (p in B and r in ['pobj', 'dobj'])
                                or (P[p] in B and R[p] in ['pobj', 'dobj']) and r == 'conj'):
                            D[i] = True
                        if ((i in ETS and r in ['nsubj', 'nsubjpass'])
                                or (i in ETS and r in ['poss', 'advmod'])):
                            D[p] = True
                        if (Tc[p] == 'VERB' and r == 'dobj'):
                            B[p] = True
                    NEW_LEN_BD = len(B) + len(D)
                    CONVERGED = (NEW_LEN_BD == OLD_LEN_BD)
            out_mention["sentences"][m_idx]["d"] = D
            out_data[entity].append(out_mention)
    ns.out_data = out_data
