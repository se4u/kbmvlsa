#!/usr/bin/env python
'''
| Filename    : wikimic_identify_governors.pkl.py
| Description : Identify Governors according to the dependency relations.
| Author      : Pushpendre Rastogi
| Created     : Thu Aug  4 03:06:45 2016 (-0400)
| Last-Updated: Fri Aug  5 15:56:56 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 31
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
arg_parser.add_argument('--debug_print', default=1, type=int)
args = arg_parser.parse_args()


def unwrap_mention(m_list):
    for m in m_list:
        yield (m["s"], m["p"], m["r"])

with open(args.in_fn) as in_f, rasengan.open_wmdoe(args.out_fn) as out_f:
    for entity, mentions in sPickle.s_load(in_f):
        out_mentions = []
        for mention in mentions:
            for m_idx, (sent, parse, referents) in enumerate(
                    unwrap_mention(mention["sentences"])):
                parse = [_.strip().split('\t') for _ in parse]
                D = rasengan.entity_descriptors(
                    referents, parse, debug_print=args.debug_print)
                mention["sentences"][m_idx]["d"] = D
                pass
            out_mentions.append(mention)
            pass
        sPickle.s_dump_elt((entity, out_mentions), out_f)
