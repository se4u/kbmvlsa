#!/usr/bin/env python
'''
| Filename    : wikilink_category_to_url_and_count_reverse_index.py
| Description : Create a memory efficient object that can serve as a reverse index.
| Author      : Pushpendre Rastogi
| Created     : Mon Aug 29 15:13:48 2016 (-0400)
| Last-Updated: Mon Aug 29 16:00:09 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 9
'''
from collections import defaultdict, MutableMapping
import cPickle as pkl
import rasengan


class WikilinkReverseIndex(MutableMapping):

    def __init__(self, ci, url_to_cat_cnt, admissible_url=None):
        self.ci = ci
        self.ic = dict((b, a) for (a, b) in self.ci.iteritems())
        urli = {}
        self.cat2url = defaultdict(list)
        static_url_idx = 0
        for url, (cats, cnt) in url_to_cat_cnt.iteritems():
            if (admissible_url is not None) and (url not in admissible_url):
                continue
            try:
                url_idx = urli[url]
            except KeyError:
                urli[url] = static_url_idx
                url_idx = static_url_idx
                static_url_idx += 1
                pass
            for cat_idx in cats:
                self.cat2url[cat_idx].append([url_idx, cnt])
        self.cat2url.default_factory = None  # FINALIZE!! cat2url
        self.iurl = dict((b, a) for (a, b) in urli.iteritems())
        del urli
        return

    def __getitem__(self, cat):
        return [[self.iurl[url_idx], cnt] for url_idx, cnt in self.cat2url[self.ci[cat]]]

    def __setitem__(self, _k, _v):
        raise NotImplementedError

    def __delitem__(self, k):
        raise NotImplementedError

    def __len__(self):
        return len(self.cat2url)

    def __iter__(self):
        return (self.ic[e] for e in self.cat2url)


def main():
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--ci_pkl_fn', default='data/dbpedia_cat_index.pkl', type=str)
    arg_parser.add_argument(
        '--wdc_pkl_fn', default='data/wikilink_dbpedia_categories.pkl', type=str)
    arg_parser.add_argument(
        '--out_pkl_fn', default='data/wikilink_category_to_url_and_count_reverse_index.pkl', type=str)
    arg_parser.add_argument(
        '--out_tsv_fn', default='data/wikilink_category_to_count.tsv', type=str)
    arg_parser.add_argument(
        '--admissible_url_fn', default='data/dbpedia_people.list', type=str)
    args = arg_parser.parse_args()
    with rasengan.tictoc('Loading pkl'):
        ci = pkl.load(open(args.ci_pkl_fn))
        url_to_cat_cnt = pkl.load(open(args.wdc_pkl_fn))
        admissible_url = set([e.strip() for e in open(args.admissible_url_fn)])
    with rasengan.tictoc('Creating WRI'):
        wri = WikilinkReverseIndex(ci, url_to_cat_cnt, admissible_url)
    with open(args.out_tsv_fn, 'w') as f:
        for (a, b) in wri.iteritems():
            f.write('%s\t%d\t%d\n'%(a, len(b), sum([e[1] for e in b])))
    with open(args.out_pkl_fn, 'wb') as f:
        pkl.dump(wri, f)
if __name__ == '__main__':
    main()
