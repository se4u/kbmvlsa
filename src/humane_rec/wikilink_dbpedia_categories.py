#!/usr/bin/env python
'''
| Filename    : categories.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Aug 29 11:36:21 2016 (-0400)
| Last-Updated: Mon Aug 29 12:39:49 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 25
'''
import cPickle as pkl
import os.path
import bz2
import rasengan
from collections import defaultdict
opj = os.path.join
dbpdir = os.path.expanduser('~/Downloads/dbpedia')
dbpedia_pref_len = len('<http://dbpedia.org/resource/')
cat_pref_len = len('Category:')
wiki_https_pref = 'https://en.wikipedia.org/wiki/'
wiki_http_pref = 'http://en.wikipedia.org/wiki/'


def simplify_wiki_url(url):
    return url.replace(wiki_http_pref, '').replace(wiki_https_pref, '')

cat_index = {}
row_idx = 0
with rasengan.tictoc('Loading Category Index'): # 100s
    for row in bz2.BZ2File(opj(dbpdir, 'article_categories_en.ttl.bz2')):
        if row.startswith('#'):
            continue
        row = row.strip().split()
        cat = row[2][dbpedia_pref_len + cat_pref_len:-1]
        if cat not in cat_index:
            cat_index[cat] = row_idx
            row_idx += 1
            
with open('data/dbpedia_cat_index.pkl', 'wb') as f:
    pkl.dump(cat_index, f)


with rasengan.tictoc('Loading Article Categories'): # 121s
    art_cat = defaultdict(list)
    for row in bz2.BZ2File(opj(dbpdir, 'article_categories_en.ttl.bz2')):
        # '''<http://dbpedia.org/resource/Albedo> <http://purl.org/dc/terms/subject>
        # <http://dbpedia.org/resource/Category:Climate_forcing> .'''
        if row.startswith('#'):
            continue
        row = row.strip().split()
        c, d = row[0], row[2]
        c = c[dbpedia_pref_len:-1]
        d = d[dbpedia_pref_len + cat_pref_len: -1]
        art_cat[hash(c)].append(cat_index[d])
        pass
    art_cat = dict(art_cat)

with rasengan.tictoc('Loading Redirects'): # 36s
    redirect = {}
    for row in bz2.BZ2File(opj(dbpdir, 'redirects_en.ttl.bz2')):
        # ''''<http://dbpedia.org/resource/AccessibleComputing>
        # <http://dbpedia.org/ontology/wikiPageRedirects>
        # <http://dbpedia.org/resource/Computer_accessibility> .'''
        if row.startswith('#'):
            continue
        row = row.strip().split()
        a, b = row[0], row[2]
        a = a[dbpedia_pref_len:-1]
        b = b[dbpedia_pref_len:-1]
        redirect[hash(a)] = b
        pass


data = pkl.load(open('data/wiki_link_url_counts.pkl'))
processed_data = {}
for (url, count) in data.iteritems():
    url = simplify_wiki_url(url)
    try:
        url = redirect[hash(url)]
    except:
        pass
    try:
        cats = art_cat[hash(url)]
    except KeyError:
        continue
    processed_data[url] = (cats, count)

with open('data/wikilink_dbpedia_categories.pkl', 'wb') as f:
    pkl.dump(processed_data, f)
