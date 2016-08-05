#!/usr/bin/env python
'''
| Filename    : wikimic_tokenize_parse_sentence.pkl.py
| Description : Convert the parsed conll files into a pickle-dict format.
| Author      : Pushpendre Rastogi
| Created     : Wed Aug  3 22:46:50 2016 (-0400)
| Last-Updated: Thu Aug  4 21:15:37 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 66
'''
import cPickle as pickle
import gzip
import itertools
import argparse
from rasengan import reshape_conll, tictoc, debug_support

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
    sent_to_parse_map = {}
    with tictoc("Reading Parses"):
        with gzip.open(args.in_sent_gz) as f, gzip.open(args.in_parse_gz) as f2:
            for sent, _parse in itertools.izip(
                    f,
                    (_parse
                     for (_k, _parse)
                     in itertools.groupby(f2, lambda row: row != '\n')
                     if _k)):
                # It is trivial to implement error checking at this step.
                # Ideally I will just use the hash of the sentence to
                sent_to_parse_map[hash(sent.strip())] = list(_parse)
    data = pickle.load(open(args.in_fn))
    out_data = {}
    with debug_support():
        for entity in data:
            out_data[entity] = []
            for mention in data[entity]:
                mention["e_sent_idx"] = mention["e_sent"]
                del mention["e_sent"]
                mention["sentences"] = [dict(s=s,
                                             p=sent_to_parse_map[hash(s.strip())])
                                        for s
                                        in mention["sentences"]]
                out_data[entity].append(mention)

    with open(args.out_fn, "wb") as f:
        pickle.dump(out_data, f)
