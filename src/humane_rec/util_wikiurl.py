'''
| Filename    : util_wikiurl.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Wed Sep  7 11:18:00 2016 (-0400)
| Last-Updated: Wed Sep  7 12:48:04 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 4
'''
wiki_https_pref = 'https://en.wikipedia.org/wiki/'
wiki_http_pref = 'http://en.wikipedia.org/wiki/'
def simplify_wiki_url(url):
    return url.replace(wiki_http_pref, '').replace(wiki_https_pref, '')

def get_redirect():
    import os.path
    import bz2
    DBPEDIA_PREF_LEN = len('<http://dbpedia.org/resource/')
    DBPDIR = os.path.expanduser('~/Downloads/dbpedia')
    redirect = {}
    for row in bz2.BZ2File(os.path.join(DBPDIR, 'redirects_en.ttl.bz2')):
        # ''''<http://dbpedia.org/resource/AccessibleComputing>
        # <http://dbpedia.org/ontology/wikiPageRedirects>
        # <http://dbpedia.org/resource/Computer_accessibility> .'''
        if row.startswith('#'):
            continue
        row = row.strip().split()
        a, b = row[0], row[2]
        a = a[DBPEDIA_PREF_LEN:-1]
        b = b[DBPEDIA_PREF_LEN:-1]
        redirect[hash(a)] = b
    return redirect
