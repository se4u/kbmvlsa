#!/usr/bin/env python3
'''
| Filename    : mention_and_type_to_wikilink.py
| Description : Denormalize the ACE and ACEtoWIKI data.
| Author      : Pushpendre Rastogi
| Created     : Tue Jul 12 11:32:31 2016 (-0400)
| Last-Updated: Thu Jul 14 04:30:16 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 86
'''
from config import ACEtoWIKI, ACE, sanitize_doc, sanitize_doc_inverse
import rasengan
import pickle
import os
import re
from bs4 import BeautifulSoup
import argparse
arg_parser = argparse.ArgumentParser(
    description='Denormalize ACE, ACEtoWiki data')
arg_parser.add_argument('--wikilink_category_pkl_fn',
                        default="data/wikilink_category.pkl", type=str)
arg_parser.add_argument('--document_to_sentence_pkl_fn',
                        default="data/ace_document_to_sentence.pkl", type=str)
arg_parser.add_argument(
    '--out_file', default="data/mention_and_type_to_wikilink", type=str)
args = arg_parser.parse_args()
# ------------------------------------------------------- #
# Map from Document to [wikilink, mention, head location] #
# ------------------------------------------------------- #
a2w = rasengan.pivot_lol_by_col(
    [e.strip().split('\t')
     for e
     in open(ACEtoWIKI, encoding='utf-8').readlines()],
    1)

# ------------------------------------------------- #
# Make sure that the documents exist in ACE corpus. #
# ------------------------------------------------- #
ace_files = set(os.listdir(ACE))
for fn in a2w:
    assert fn in ace_files

# ----------------------------- #
# Map from wikilink to category #
# ----------------------------- #
wikilink_to_category = pickle.load(
    open(args.wikilink_category_pkl_fn, "rb"))['link_to_category']

# --------------------------------------- #
# Map from sgm document to its sentences. #
# --------------------------------------- #
doc_to_sentence = pickle.load(open(args.document_to_sentence_pkl_fn, 'rb'))


class BadAnnotation(Exception):
    pass


def get_sentence_around(sgm_fn, start, stop):
    '''Get a soup object and a span the sentence around which needs to be
    extracted. The sentence extraction itself does not need to be super fancy.
    Even basic methods will be fine, since the sentences need to be parsed later
    on anyway.
    '''
    doc = doc_to_sentence[sgm_fn]
    for b, e, s in doc:
        if b <= start and e >= stop:
            return (s, b, e)
    raise BadAnnotation


# ------------------------------------------------------------------ #
# Extract the mention type, entity type, entity subtype for mention. #
# ------------------------------------------------------------------ #
out_f = open(args.out_file, 'w', encoding='utf-8')
with rasengan.debug_support():
    bad_sgm_fn = []
    bad_categories = []
    mention_lost = 0
    for sgm_fn in a2w:
        doc_name = sgm_fn[:-4]
        annotation = BeautifulSoup(
            sanitize_doc(open(os.path.join(ACE, doc_name + '.apf.xml'),
                              encoding='utf-8').read()),
            'html.parser')
        for (link, entity_id_suffix, head_loc) in a2w[sgm_fn]:
            # Find head with entity.entity_mention.head.charseq[START] =
            # head_loc
            expected_entity_id = doc_name + '-' + entity_id_suffix
            heads = [e
                     for e
                     in annotation.find_all('head')
                     if e.charseq['start'] == head_loc
                     and e.parent.parent['id'] == expected_entity_id]
            if len(heads) != 1:
                print ('head problem', sgm_fn)
            head = heads[0]
            entity_mention = head.parent
            entity = entity_mention.parent
            start = int(head.charseq['start'])
            end = int(head.charseq['end']) + 1

            try:
                sent, begin_sent, end_sent = get_sentence_around(
                    sgm_fn, start, end)
            except BadAnnotation:
                if sgm_fn != 'misc.legal.moderated_20050129.2225.sgm':
                    import pdb
                    pdb.set_trace()
                continue
            begin_ent = start - begin_sent
            end_ent = end - begin_sent
            expected_str = sanitize_doc_inverse(
                head.charseq.string)
            if ((expected_str != sent[begin_ent:end_ent])
                and (sgm_fn not in ['BACONSREBELLION_20050226.1317.sgm',
                                    'CNN_ENG_20030616_130059.25.sgm'])):
                mention_lost += 1
                print(
                    sgm_fn, start, end - 1, head.charseq.string, sent[begin_ent:end_ent])
            else:
                sent = sent.replace('\n', ' ')
                if (sgm_fn not in ['BACONSREBELLION_20050226.1317.sgm',
                                   'CNN_ENG_20030616_130059.25.sgm']):
                    assert (expected_str.replace('\n', ' ') == sent[begin_ent:end_ent]), str(
                        (expected_str, sent[begin_ent:end_ent]))
                    # NOTE: Now we know the sentence, its beginning and ending
                    # and the type of entity.
                    if 'http' not in link:
                        categories = ''
                    else:
                        categories = []
                        for l in link.replace('http://en.wikipedia.org/wiki/', '').split():
                            l = re.sub(r'[^\x00-\x7F]',
                                       lambda c: rasengan.unicode_to_utf8_hex(
                                           c.group(0)),
                                       l).replace('#', '%23')
                            if l in wikilink_to_category:
                                categories += wikilink_to_category[l]
                            else:
                                bad_categories.append(l)
                                print (l)
                        categories = ';'.join(categories)
                    out_f.write(' ||| '.join([sgm_fn,
                                              entity['id'],
                                              entity['type'],
                                              entity['subtype'],
                                              entity_mention['type'],
                                              str(begin_ent),
                                              str(end_ent),
                                              sent,
                                              link,
                                              categories]))
                    out_f.write('\n')
    print (set(bad_sgm_fn), set(bad_categories), mention_lost)
