#!/usr/bin/env python
'''
| Filename    : wikimic_create_entity_token_set.pkl.py
| Description : Identify the entity token and tokens that co-refer to the entity token.
| Author      : Pushpendre Rastogi
| Created     : Wed Aug  3 23:35:30 2016 (-0400)
| Last-Updated: Fri Aug  5 12:25:58 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 29
'''
import rasengan
from rasengan import sPickle
import argparse
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument(
    '--in_fn', default='data/wikimic_tokenize_parse_sentence.spkl', type=str)
arg_parser.add_argument(
    '--out_fn', default='data/wikimic_create_entity_token_set.spkl', type=str)
arg_parser.add_argument('--pronomial_coref', default=1, type=int)
args = arg_parser.parse_args()


def get_tokens_from_conll(p):
    return [row.split('\t')[1] for row in p]

with open(args.in_fn) as in_f, open(args.out_fn, 'wb') as out_f:
    for (entity, mentions) in sPickle.s_load(in_f):
        canonical_mention = rasengan.html_entity_to_unicode(
            entity.split('/')[-1].lower()).split('_')
        out_mentions = []
        for mention in mentions:
            for idx in range(len(mention["sentences"])):
                mention["sentences"][idx]["r"] = {}
            e_sent_idx = mention["e_sent_idx"]
            e_tokens = get_tokens_from_conll(
                mention["sentences"][e_sent_idx]["p"])
            lot = rasengan.tokens_in_tokenization_corresponding_to_a_span(
                sent=mention["sentences"][e_sent_idx]["s"],
                start=mention["e_start"],
                end=mention["e_end"],
                tokens=e_tokens)
            mention["lot"] = lot
            referents = rasengan.get_referents(
                e_sent_idx,
                canonical_mention,
                lot[1],
                [get_tokens_from_conll(e['p']) for e in mention['sentences']],
                pronomial_coref=args.pronomial_coref)
            # -- Add tokens in the "href" if they are less than 4. -- #
            # if lot[1] - lot[0] <= 4:
            #     for t in lot:
            #         mention["sentences"][e_sent_idx]["r"][t] = True
            # Add the referents found in other sentences.
            for (r_s_idx, r_t_idx) in referents:
                mention["sentences"][r_s_idx]["r"][r_t_idx] = None
            out_mentions.append(mention)
            pass
        sPickle.s_dump_elt((entity, out_mentions), out_f)
