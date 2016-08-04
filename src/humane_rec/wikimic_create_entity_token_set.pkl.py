#!/usr/bin/env python
'''
| Filename    : wikimic_create_entity_token_set.pkl.py
| Description : Identify the entity token and tokens that co-refer to the entity token.
| Author      : Pushpendre Rastogi
| Created     : Wed Aug  3 23:35:30 2016 (-0400)
| Last-Updated: Thu Aug  4 10:31:29 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 10
'''
import rasengan
with rasengan.pklflow_ctx(
        in_fn="data/wikimic_tokenize_parse_sentence.pkl",
        out_fn="data/wikimic_create_entity_token_set.pkl") as ns:
    data = ns.data
    out_data = {}
    for entity, mentions in data.iteritems():
        out_data[entity] = []
        canonical_mention = rasengan.html_entity_to_unicode(
            entity.split('/')[-1].lower()).split('_')
        for mention in mentions:
            out_mention = mention
            for idx in range(len(mention["sentences"])):
                out_mention["sentences"][idx]["r"] = {}
            e_sent_idx = mention["e_sent_idx"]
            e_tokens = mention["sentences"][e_sent_idx]["p"][1]
            lot = rasengan.tokens_in_tokenization_corresponding_to_a_span(
                sent=mention["sentences"][e_sent_idx]["s"],
                start=mention["e_start"],
                end=mention["e_end"],
                tokens=e_tokens)
            out_mention["lot"] = lot
            referents = rasengan.get_referents(
                e_sent_idx,
                canonical_mention,
                lot[1],
                [[e[1] for e in _[1]] for _ in mention["sentences"]])
            # Add the canonical tokens
            if lot[1] - lot[0] <= 4:
                for t in lot:
                    out_mention["sentences"][e_sent_idx]["r"][t] = True
            else:
                for t in lot:
                    if e_tokens[t].lower() in canonical_mention:
                        out_mention["sentences"][e_sent_idx]["r"][t] = True
            # Add the referents found in other sentences.
            for (r_s_idx, r_t_idx) in referents:
                out_mention["sentences"][r_s_idx]["r"][r_t_idx] = True
            out_data[entity].append(out_mention)
    ns.out_data = out_data
