#!/usr/bin/env python
'''
| Filename    : catpeople_clean_segmented_context.py
| Description : Remove nonascii characters, Segment sentences, remove noisy long sentences.
| Author      : Pushpendre Rastogi
| Created     : Sun Sep  4 16:58:25 2016 (-0400)
| Last-Updated: Wed Sep  7 19:31:57 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 52
'''
from rasengan import clean_text, sentence_segmenter, tictoc, get_tokenizer, TokenMapper, \
    tokens_in_tokenization_corresponding_to_a_span, deduplicate_unhashables

from shelve import DbfilenameShelf
import argparse
import sys, os
arg_parser = argparse.ArgumentParser(
    description='Remove junk from catpeople wikimic')
arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
arg_parser.add_argument('--MAX_CHAR_IN_SENT', default=1000, type=int)
PDIR = ('/export/b15/prastog3' if os.uname()[1] == 'b15' else 'data/')
arg_parser.add_argument(
    '--in_shelf', default='%s/catpeople_wikilink_mentions.shelf'%PDIR, type=str)
arg_parser.add_argument(
    '--out_shelf', default='%s/catpeople_clean_segmented_context.shelf'%PDIR, type=str)
args = arg_parser.parse_args()
in_shelf = DbfilenameShelf(args.in_shelf, protocol=-1, flag='r')
out_shelf = DbfilenameShelf(args.out_shelf, protocol=-1)
urls = in_shelf['__URL_LIST__']

PAT_TOKENIZER = get_tokenizer()
TOKEN_MAPPER = TokenMapper()
MAX_CHAR_IN_SENT = args.MAX_CHAR_IN_SENT
import re
MIDDLE_NAME_REGEX = re.compile('[A-Z][^ ]*? [A-Z]\. [A-Z]')
for url_idx, url in enumerate(urls):
    print >> sys.stderr, ('Done: %.3f \r'%(float(url_idx)*100/len(urls))) ,
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
            # We usually skip mention texts that a sentence
            # segmenter would segment because those are usually
            # completely sentences or noisy sentences that have
            # been linked to entities. Such things are usually
            # useless.
            if (len(mention[1]) < 30) or MIDDLE_NAME_REGEX.match(mention[1]):
                seg[e_sent] = (seg[e_sent][0], seg[e_sent2][1])
                for e_sent_tok_idx in range(e_sent2, e_sent, -1):
                    del seg[e_sent_tok_idx]
            else:
                # import pdb; pdb.set_trace()
                print >> sys.stderr, "Skipped mention", mention[1]
                continue
        if seg[e_sent][1] - seg[e_sent][0] > MAX_CHAR_IN_SENT:
            # The sentence that contains the entity is too long.
            print >> sys.stderr, '__noisy__', text[
                seg[e_sent][0]:seg[e_sent][1]]
            continue
        e_start = mention_start - seg[e_sent][0]
        # Remove too long sentences.
        sentences = [[tmp_tok.lower() for tmp_tok in PAT_TOKENIZER(text[a:b])]
                     for (a, b) in seg
                     if b - a <= MAX_CHAR_IN_SENT]
        mapped_sentences = [TOKEN_MAPPER(e) for e in sentences]
        # Adjust pointer to sentence that contain the entity since we
        # might have removed some extremely long sentences.
        # idx_to_sentence_that_contains_entity
        itste = (e_sent
                 - sum(1 for (a, b)
                       in seg[:e_sent]
                       if b - a > MAX_CHAR_IN_SENT))
        esidx, eeidx = tokens_in_tokenization_corresponding_to_a_span(
            text[seg[itste][0]:seg[itste][1]],
            e_start,
            e_start + len_mention,
            sentences[itste])
        out_mention = [mapped_sentences, itste, esidx, eeidx]
        out_mentions.append(out_mention)
        pass
    out_shelf[url] = deduplicate_unhashables(out_mentions)
out_shelf['__URL_LIST__'] = urls
out_shelf['__TOKEN_MAPPER__'] = TOKEN_MAPPER
out_shelf.close()
