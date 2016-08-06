#!/usr/bin/env python
'''
| Filename    : demonstrate_similarity_idea.emb.py
| Description : Create a small embeddings file that we can store in the data directory and that can be loaded easily.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 22:01:10 2016 (-0400)
| Last-Updated: Fri Aug  5 18:16:23 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 21
'''
import cPickle as pkl
# import rasengan, yaml
# yaml_data = yaml.load(open('data/women_writer_manual_clues.yaml'))
# tags = set(
# rasengan.flatten([(rasengan.flatten(b[1::2])) for b in
# yaml_data.values()]))

tags = {}
entities = list(e.strip()
                for e in open('data/category_to_entities/American_women_writers'))
for row in open('data/entity_descriptors_procoref~0.psv'):
    entity, _tags = [e.strip() for e in row.strip().split('|||')]
    if entity in entities:
        for t in (e.strip().split(':')[0] for e in _tags.split()):
            tags[t.lower()] = None
            pass
        pass
    pass
# print tags.keys()

data = pkl.load(open(
    '/Users/pushpendrerastogi/data/embedding/mvlsa/combined_embedding_0.emb.pkl'))
tag_emb = {}
for tag in tags:
    try:
        tag_emb[tag] = data[tag]
    except KeyError:
        print tag
with open('data/demonstrate_similarity_idea.emb.pkl', 'wb') as f:
    pkl.dump(tag_emb, f, protocol=-1)
