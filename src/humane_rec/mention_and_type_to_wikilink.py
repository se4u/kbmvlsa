#!/usr/bin/env python3
'''
| Filename    : mention_and_type_to_wikilink.py
| Description : Denormalize the ACE and ACEtoWIKI data.
| Author      : Pushpendre Rastogi
| Created     : Tue Jul 12 11:32:31 2016 (-0400)
| Last-Updated: Wed Jul 13 02:38:17 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 23
'''
from config import ACEtoWIKI, ACE
import rasengan
import pickle
import os
import sys
from bs4 import BeautifulSoup

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
pkl = pickle.load(open("data/wikilink_category.pkl", "rb"))
# category_to_link=pkl['category_to_link']
wikilink_to_category = pkl['link_to_category']


def get_sentence_around(sgm, span):
    '''Get a soup object and a span the sentence around which needs to be
    extracted. The sentence extraction itself does not need to be super fancy.
    Even basic methods will be fine, since the sentences need to be parsed later
    on anyway.
    '''
    pass
# ------------------------------------------------------------------ #
# Extract the mention type, entity type, entity subtype for mention. #
# ------------------------------------------------------------------ #
with rasengan.debug_support():
    for sgm_fn in a2w:
        sgm = BeautifulSoup(
            open(os.path.join(ACE, sgm_fn), encoding='utf-8').read(),
            'html.parser')
        doc_name = sgm_fn[:-4]
        annotation = BeautifulSoup(
            open(os.path.join(ACE, doc_name + '.apf.xml'),
                 encoding='utf-8').read(),
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
            assert len(heads) == 1
            head = heads[0]
            entity_mention = head.parent
            entity = entity_mention.parent
            start = int(head.charseq['start'])
            end = int(head.charseq['end'])
            print (entity['id'],
                   entity['type'],
                   entity['subtype'],
                   entity_mention['type'],
                   start,
                   end,
                   head.charseq.string,
                   sgm.get_text()[start - 1:end + 1])
            print get_sentence_around(sgm, (start - 1, end + 1))
            # NOTE: Getting the sentence will complete this step of the pipeline.
            # Parsey requires python2 and syntaxnet requires docker etc.
            # Those things are better done in a separate step.
