#!/usr/bin/env python
'''
| Filename    : unique_human_entities_wikidata_id.py
| Description : Acquire Wikidata IDs for urls listed in input file.
| Author      : Pushpendre Rastogi
| Created     : Wed Jul 20 20:43:01 2016 (-0400)
| Last-Updated: Thu Jul 21 00:11:44 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 20
'''
import os
from rasengan import wiki_encode_url, flatfile_to_dict, debug_support, cache_to_disk
import requests
import argparse

session = requests.Session()
arg_parser = argparse.ArgumentParser(description='')
arg_parser.add_argument('--human_entity_url_fn',
                        default='data/unique_human_entities', type=str)
arg_parser.add_argument('--wikidata_to_freebase_id_fn',
                        default='~/data/freebase_to_wikidata/freebase_to_wikidata.compressed',
                        type=str)
arg_parser.add_argument(
    '--shelf_fn', default='data/unique_human_entities_wikidata_id.cache', type=str)
arg_parser.add_argument(
    '--out_fn', default='data/unique_human_entities_wikidata_id', type=str)
args = arg_parser.parse_args()

d = flatfile_to_dict(os.path.expanduser(args.wikidata_to_freebase_id_fn))


@cache_to_disk(shelf_fn=args.shelf_fn)
def get_data_over_internet(url):
    return session.get(url).json()
with debug_support():
    with open(args.out_fn, 'w', encoding='utf-8') as out_f:
        wiki_url_to_wikidata_id_map = {}
        with open(args.human_entity_url_fn) as in_f:
            for wiki_url in in_f:
                wiki_url = wiki_url.strip()
                title = wiki_encode_url(
                    wiki_url.replace('http://en.wikipedia.org/wiki/', ''))
                wikipedia_request = 'https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=pageprops&ppprop=wikibase_item&redirects&format=json' % title
                data = get_data_over_internet(wikipedia_request)
                wikidata_id = (
                    list(data['query']['pages'].values())[0]['pageprops']['wikibase_item'])
                wiki_url_to_wikidata_id_map[wiki_url] = wikidata_id
        for (wiki_url, wikidata_id) in wiki_url_to_wikidata_id_map.items():
            try:
                freebase_mid = d[wikidata_id]
            except KeyError:
                wikidata_request = 'https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=%s&property=P646&props=&format=json' % wikidata_id
                data = get_data_over_internet(wikidata_request)
                freebase_mid = (
                    data['claims']['P646'][0]['mainsnak']['datavalue']['value']
                    if 'P646' in data['claims']
                    else 'NOT_IN_FREEBASE')
            out_f.write('%s %s\n' % (wiki_url, freebase_mid))

# Close the shelf.
get_data_over_internet.shelf.close()
