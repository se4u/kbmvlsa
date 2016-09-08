#!/usr/bin/env python
'''
| Filename    : categories.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Mon Aug 29 11:36:21 2016 (-0400)
| Last-Updated: Wed Sep  7 12:41:05 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 28
'''
import cPickle as pkl
import os.path
import bz2
import rasengan
from collections import defaultdict
opj = os.path.join
dbpdir = os.path.expanduser('~/Downloads/dbpedia')
from util_wikiurl import simplify_wiki_url
DBPEDIA_PREF_LEN = len('<http://dbpedia.org/resource/')
CAT_PREF_LEN = len('Category:')

cat_index = {}
row_idx = 0
with rasengan.tictoc('LOADING CATEGORY INDEX FROM DBPEDIA'): # 100s
    for row in bz2.BZ2File(opj(dbpdir, 'article_categories_en.ttl.bz2')):
        # Discard rows that start with '#' since they are comments.
        if row.startswith('#'):
            continue
        row = row.strip().split()
        cat = row[2][DBPEDIA_PREF_LEN + CAT_PREF_LEN:-1]
        if cat not in cat_index:
            cat_index[cat] = row_idx
            row_idx += 1

with open('data/dbpedia_cat_index.pkl', 'wb') as f:
    pkl.dump(cat_index, f)


with rasengan.tictoc('LOADING ARTICLE to CATEGORY MAP FROM DBPEDIA'): # 121s
    art_cat = defaultdict(list)
    for row in bz2.BZ2File(opj(dbpdir, 'article_categories_en.ttl.bz2')):
        # '''<http://dbpedia.org/resource/Albedo> <http://purl.org/dc/terms/subject>
        # <http://dbpedia.org/resource/Category:Climate_forcing> .'''
        if row.startswith('#'):
            continue
        row = row.strip().split()
        c, d = row[0], row[2]
        c = c[DBPEDIA_PREF_LEN:-1]
        d = d[DBPEDIA_PREF_LEN + CAT_PREF_LEN: -1]
        art_cat[hash(c)].append(cat_index[d])
        pass
    art_cat = dict(art_cat)

with rasengan.tictoc('LOADING REDIRECTS'): # 36s
    from util_wikiurl import get_redirect
    redirect = get_redirect()


# ------------------------------------------------------ #
# Filter the dbpedia article_to_category table `art_cat` #
# to keep only the urls that appear in wiki_links data   #
# ------------------------------------------------------ #
data = pkl.load(open('data/wiki_link_url_counts.pkl'))
processed_data = {}
for (url, count) in data.iteritems():
    url = simplify_wiki_url(url)

    # Follow url redirect.
    try: url = redirect[hash(url)]
    except KeyError: pass

    # Get categories from article.
    try: cats = art_cat[hash(url)]
    except KeyError: continue

    processed_data[url] = (cats, count)

with open('data/wikilink_dbpedia_categories.pkl', 'wb') as f:
    pkl.dump(processed_data, f)
