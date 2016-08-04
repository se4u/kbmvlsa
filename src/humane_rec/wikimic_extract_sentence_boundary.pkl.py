#!/usr/bin/env python
'''
| Filename    : wikimic_extract_sentence_boundary.pkl.py
| Description : Extract sentence boundaries from the mentions.
| Author      : Pushpendre Rastogi
| Created     : Wed Aug  3 16:49:48 2016 (-0400)
| Last-Updated: Wed Aug  3 22:41:10 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 21
'''
from rasengan import pklflow_ctx, sentence_segmenter
import sys

with pklflow_ctx(in_fn="data/wikimic_remove_translate_nonascii.pkl",
                 out_fn="data/wikimic_extract_sentence_boundary.pkl") as ns:
    out_data = {}
    for entity, mentions in ns.data.iteritems():
        out_data[entity] = []
        for mention in mentions:
            mention = [e.replace('\n', '') for e in mention]
            out_mention = []
            # As Version 1, we use the nltk sentence boundary detector.
            text = ' '.join(mention)
            seg = sentence_segmenter(text)
            # Add 1 to mention_start for the space we just added
            mention_start = len(mention[0]) + 1
            len_mention = len(mention[1])
            mention_end = mention_start + len_mention
            entity_start_seg = max(
                [i for i, e in enumerate(seg) if mention_start >= e[0]])
            entity_end_seg = min(
                [i for i, e in enumerate(seg) if mention_end <= e[1]])
            if entity_start_seg != entity_end_seg:
                print >> sys.stderr, "Skipped mention", mention[1]
                continue
            e_sent = entity_start_seg
            e_start = mention_start - seg[e_sent][0]
            out_mention = dict(
                sentences=[text[a:b] for (a, b) in seg],
                e_sent=e_sent,
                e_start=e_start,
                e_end=e_start + len_mention)
            out_data[entity].append(out_mention)
    ns.out_data = out_data
