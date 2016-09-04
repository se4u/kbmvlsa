#!/usr/bin/env python
'''
| Filename    : catpeople_clean_segmented_context.py
| Description : Remove nonascii characters, Segment sentences, remove noisy long sentences.
| Author      : Pushpendre Rastogi
| Created     : Sun Sep  4 16:58:25 2016 (-0400)
| Last-Updated: Sun Sep  4 19:04:17 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 17
'''
from rasengan import clean_text, sentence_segmenter, tictoc
from shelve import DbfilenameShelf
import argparse
import sys
arg_parser = argparse.ArgumentParser(
    description='Remove junk from catpeople wikimic')
arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
arg_parser.add_argument(
    '--in_shelf', default='data/catpeople_wikilink_mentions.shelf', type=str)
arg_parser.add_argument(
    '--out_shelf', default='data/catpeople_clean_segmented_context.shelf', type=str)
arg_parser.add_argument('--MAX_CHAR_IN_SENT', default=1000, type=int)
args = arg_parser.parse_args()
in_shelf = DbfilenameShelf(args.in_shelf, protocol=-1, flag='r')
out_shelf = DbfilenameShelf(args.out_shelf, protocol=-1)
urls = in_shelf['__URL_LIST__']
MAX_CHAR_IN_SENT = args.MAX_CHAR_IN_SENT

for url in urls:
    with tictoc('Processing ' + url, override='stderr'):
        mentions = in_shelf[url]
        out_mentions = []
        for mention in mentions:
            # ------------------------------ #
            # Clean The Text of the mentions #
            # ------------------------------ #
            mention = [clean_text(text).replace('\n', '')
                       for text in mention]
            # ---------------------------------- #
            # Segment the mention into sentences #
            # ---------------------------------- #
            # Preamble
            # Add 1 for the space we will add
            mention_start = len(mention[0]) + 1
            len_mention = len(mention[1])
            mention_end = mention_start + len_mention
            text = ' '.join(mention)
            seg = sentence_segmenter(text)
            e_sent = max(
                [i for i, e in enumerate(seg) if mention_start >= e[0]])
            e_sent2 = min(
                [i for i, e in enumerate(seg) if mention_end <= e[1]])
            if e_sent != e_sent2:
                print >> sys.stderr, "Skipped mention", mention[1]
                continue
            if seg[e_sent][1] - seg[e_sent][0] > MAX_CHAR_IN_SENT:
                # The sentence that contains the entity is too long.
                print >> sys.stderr, '__noisy__', text[
                    seg[e_sent][0]:seg[e_sent][1]]
                continue
            e_start = mention_start - seg[e_sent][0]
            out_mention = dict(
                sentences=[text[a:b]
                           for (a, b) in seg
                           # Remove too long sentences.
                           if b - a <= MAX_CHAR_IN_SENT],
                # Adjust pointer to sentence that contain the entity since we
                # might have removed some extremely long sentences.
                e_sent=(e_sent - sum(1 for (a, b)
                                     in seg[:e_sent] if b - a <= MAX_CHAR_IN_SENT)),
                e_start=e_start,
                e_end=e_start + len_mention)
            out_mentions.append(out_mention)
            pass
        out_shelf[url] = out_mentions
        pass
    pass
out_shelf.close()
