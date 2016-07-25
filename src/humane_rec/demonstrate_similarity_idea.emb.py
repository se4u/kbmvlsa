#!/usr/bin/env python
'''
| Filename    : demonstrate_similarity_idea.emb.py
| Description : Create a small embeddings file that we can store in the data directory and that can be loaded easily.
| Author      : Pushpendre Rastogi
| Created     : Sun Jul 24 22:01:10 2016 (-0400)
| Last-Updated: Sun Jul 24 22:02:34 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 1
'''
import yaml
import rasengan
import cPickle as pkl
yaml_data = yaml.load(open('data/women_writer_manual_clues.yaml'))
tags = set(
    rasengan.flatten([(rasengan.flatten(b[1::2])) for b in yaml_data.values()]))
data = pkl.load(open(
    '/Users/pushpendrerastogi/data/embedding/mvlsa/combined_embedding_0.emb.pkl'))
tag_emb = dict((tag, data[tag]) for tag in tags)
with open('data/demonstrate_similarity_idea.emb.pkl', 'wb') as f:
    pkl.dump(tag_emb, f, protocol=-1)
