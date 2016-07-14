#!/usr/bin/env python
'''
| Filename    : parse_mentions.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Thu Jul 14 19:25:42 2016 (-0400)
| Last-Updated: Thu Jul 14 19:39:04 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 4
'''
from predpatt import Parser, PredPatt
import argparse
import io
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--d1', default=' |||', type=str)
arg_parser.add_argument('--begin_mention_col', default=5, type=int)
arg_parser.add_argument('--end_mention_col', default=6, type=int)
arg_parser.add_argument('--sentence_col', default=7, type=int)
arg_parser.add_argument(
    '--in_fn', default='data/mention_and_type_for_individuals', type=str)
args = arg_parser.parse_args()
parser = Parser.get_instance()
with io.open(args.in_fn, encoding='utf-8') as f:
    for line in f:
        row = line.strip().split(args.d1)
        sentence = row[args.sentence_col][1:]
        begin_mention = int(row[args.begin_mention_col])
        end_mention = int(row[args.end_mention_col])
        mention = sentence[begin_mention:end_mention]
        parse = parser(sentence, tokenized=False)
        P = PredPatt(parse)
        print [I.root.text
               for I
               in P.instances
               if any((mention in e.phrase())
                      for e
                      in I.arguments)]
