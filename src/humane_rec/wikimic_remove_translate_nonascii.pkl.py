#!/usr/bin/env python
'''
| Filename    : wikimic_remove_translate_nonascii.pkl.py
| Description : Remove or translate non-ascii characters.
| Author      : Pushpendre Rastogi
| Created     : Wed Aug  3 14:33:06 2016 (-0400)
| Last-Updated: Wed Aug  3 16:53:32 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 6
'''
from rasengan import clean_text, pklflow_ctx

with pklflow_ctx(in_fn="data/wiki_link_individual_mentions.pkl",
                 out_fn="data/wikimic_remove_translate_nonascii.pkl") as ns:
    data = ns.data
    out_data = {}
    for entity, mentions in data.iteritems():
        out_data[entity] = []
        for mention in mentions:
            out_mention = []
            for text in mention:
                ct = clean_text(text)
                out_mention.append(ct)
            out_data[entity].append(out_mention)
    ns.out_data = out_data
