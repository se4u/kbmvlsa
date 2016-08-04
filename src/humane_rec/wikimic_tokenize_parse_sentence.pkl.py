#!/usr/bin/env python
'''
| Filename    : wikimic_tokenize_parse_sentence.pkl.py
| Description : Convert the parsed conll files into a pickle-dict format.
| Author      : Pushpendre Rastogi
| Created     : Wed Aug  3 22:46:50 2016 (-0400)
| Last-Updated: Thu Aug  4 10:51:28 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 26
'''
import cPickle as pickle
import gzip
import itertools
import argparse
from rasengan import reshape_conll

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--in_parse_gz', default="data/wikimic_tokenize_parse_sentence.conll.gz", type=str)
    arg_parser.add_argument(
        '--in_sent_gz', default="data/wikimic_extract_sentence_boundary.txt.gz", type=str)
    arg_parser.add_argument(
        '--in_fn', default="data/wikimic_extract_sentence_boundary.pkl", type=str)
    arg_parser.add_argument(
        '--out_fn', default="wikimic_tokenize_parse_sentence.pkl", type=str)
    args = arg_parser.parse_args()

    sent_to_idx_map = {}
    with gzip.open(args.in_sent_gz) as f:
        for idx, sent in enumerate(f):
            sent_to_idx_map[sent.strip()] = idx

    idx_to_parse_map = {}
    with gzip.open(args.in_parse_gz) as f:
        for idx, (_, _parse) in enumerate(
                itertools.groupby(f, lambda row: row == '\n')):
            idx_to_parse_map[idx] = reshape_conll(
                [e.strip().split('\t') for e in _parse])

    data = pickle.load(open(args.in_pkl))
    out_data = {}
    for entity in data:
        out_data[entity] = []
        for mention in data[entity]:
            out_mention = mention
            out_mention["e_sent_idx"] = out_mention["e_sent"]
            del out_mention["e_sent"]
            out_mention["sentences"] = [dict(s=s,
                                             p=idx_to_parse_map[sent_to_idx_map[s]])
                                        for s
                                        in mention["sentences"]]
            out_data[entity].append(out_mention)

    with open(args.out_fn, "wb") as f:
        pickle.dump(out_data, f)
