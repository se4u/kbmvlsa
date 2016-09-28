#!/usr/bin/env python
'''
| Filename    : parse_mentions.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Jul 14 19:25:42 2016 (-0400)
| Last-Updated: Thu Jul 14 20:23:02 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 22
'''
from predpatt import Parser, PredPatt
import argparse
import io, sys
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--d1', default=' |||', type=str)
arg_parser.add_argument('--begin_mention_col', default=5, type=int)
arg_parser.add_argument('--end_mention_col', default=6, type=int)
arg_parser.add_argument('--sentence_col', default=7, type=int)
arg_parser.add_argument(
    '--in_fn', default='data/mention_and_type_for_individuals', type=str)
arg_parser.add_argument('--out_fn', default='data/parsed_mentions', type=str)
args = arg_parser.parse_args()
parser = Parser.get_instance()
bad_sentence = {}
with io.open(args.out_fn, 'w', encoding='utf-8') as fout:
    with io.open(args.in_fn, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            row = line.split(args.d1)
            sentence = row[args.sentence_col][1:].rstrip()
            begin_mention = int(row[args.begin_mention_col])
            end_mention = int(row[args.end_mention_col])
            mention = sentence[begin_mention:end_mention]
            try:
                if sentence in bad_sentence:
                    raise Exception('bad sentence')
                parse = parser(sentence, tokenized=False)
                P = PredPatt(parse)
                predicates = [I.root.text
                              for I
                              in P.instances
                              if any((mention in e.phrase())
                                     for e
                                     in I.arguments)]
            except:
                bad_sentence[sentence]=1
                predicates = []
                pass
            s = ' ||| '.join([line, ';'.join(predicates)])
            fout.write(s)
            fout.write(u'\n')
# After everything print the bad_sentences
for s in bad_sentence:
    print >> sys.stderr, s
