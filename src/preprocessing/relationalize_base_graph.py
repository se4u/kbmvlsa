#!/usr/bin/env python
'''
| Filename    : relationalize_base_graph.py
| Description : Convert the data in sort_base into a relational format with people as pkey and features
| Author      : Pushpendre Rastogi
| Created     : Wed Apr 13 18:52:57 2016 (-0400)
| Last-Updated: Thu Apr 14 20:41:27 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 97
'''
import yaml
import rasengan
import ujson
import cPickle as pickle
import os
import sys
import collections
import argparse
# --------------- #
# Parse Arguments #
# --------------- #
arg_parser = argparse.ArgumentParser(
    description='Extract features from graph.')
arg_parser.add_argument(
    '--out_fn', default=None, type=str, help='Default={None}')
arg_parser.add_argument(
    '--cache_fn', default=None, type=str, help='Default={None}')
arg_parser.add_argument(
    '--leaf_fn', default=None, type=str, help='Default={None}')
args = arg_parser.parse_args()
# ------------------- #
# Initialize Globals. #
# ------------------- #
with rasengan.tictoc('Initializing Globals'):
    CFG = rasengan.deep_namespacer(
        yaml.load(open('relationalize_base_graph.yaml').read()))
    FOREIGN_NS, BASE_NS = pickle.load(
        open(args.cache_fn, 'rb'))
ORG_TYPES = ['adept-core#OrgHeadquarter',
             'adept-core#Organization',
             'adept-core#OrganizationWebsite',
             'adept-core#StartOrganization',
             'adept-core#EndOrganization',
             'adept-core#Membership',
             'adept-core#Subsidiary']
NONRELATIONAL_TYPES = ['adept-base#Date',
                       'adept-core#Crime',
                       'adept-core#GeoPoliticalEntity',
                       'adept-core#Person',
                       'adept-core#Title',
                       'adept-core#URL']

# ---------------- #
# Helper Functions #
# ---------------- #


def feature_path(tmpl):
    l = []
    try:
        for k in tmpl.keys():
            for p in feature_path(tmpl[k]):
                l.append([k] + p)
    except AttributeError:
        l = [[tmpl]]
    return l


class MissingFeature(Exception):
    pass


def extract(guid, type, path, feat_pfx):
    new_pfx = feat_pfx + '~' + path[0]
    if path[0] in FOREIGN_NS:
        fns = FOREIGN_NS[path[0]]
        try:
            new_guid = fns[guid]
        except KeyError:
            raise MissingFeature((guid, path[0]))
        if len(path) == 2 and path[0] == path[1]:
            return new_pfx, new_guid
        else:
            return extract(
                new_guid, FOREIGN_NS['type'][new_guid], path[1:], new_pfx)
    else:
        if len(path) == 1 and path[0] in [
                'adept-base#canonicalString', 'adept-base#xsdDate']:
            try:
                return feat_pfx, BASE_NS[(guid, path[0])]
            except KeyError:
                raise MissingFeature((guid, path[0]))
        elif len(path) == 2 and path[1] in [
                'adept-base#canonicalString', 'adept-base#xsdDate']:
            try:
                return new_pfx, BASE_NS[(guid, path[1])]
            except KeyError:
                raise MissingFeature((guid, path[1]))
        else:
            try:
                new_guid = BASE_NS[(guid, path[1])]
            except KeyError:
                raise MissingFeature((guid, path[1]))
            return extract(
                new_guid, FOREIGN_NS['type'][new_guid], path[2:], new_pfx)


def main():
    vertex_dict = collections.defaultdict(dict)
    edgelist = []
    for row in open(args.leaf_fn):
        guid, type = row.strip().split()
        if type in CFG.features:
            feature_template = CFG.features[type]
            path_list = feature_path(feature_template)
            # We extract features using the (guid, type, path_list)
            person_guid = person_name = person_confidence = None
            person_feat = {}
            for path in path_list:
                if path[0] == 'person' and person_guid is None:
                    person_guid = BASE_NS[(guid, path[1])]
                    person_feat['name'] = BASE_NS[
                        (person_guid, 'adept-base#canonicalString')]
                    person_feat['confidence'] = FOREIGN_NS[
                        'confidence'][person_guid]
                try:
                    feat_name, feat_val = extract(guid, type, path, '')
                    person_feat[feat_name] = feat_val
                except MissingFeature as e:
                    # print >> sys.stderr, e, path
                    pass
            assert person_guid is not None
            assert len(person_feat) > 0
            vertex_dict[person_guid].update(person_feat)
        elif type in CFG.edges:
            confidence = FOREIGN_NS['confidence'][guid]
            a = BASE_NS[(guid, CFG.edges[type][0])]
            b = BASE_NS[(guid, CFG.edges[type][1])]
            edge = (a, b, type, confidence)
            edgelist.append(edge)
        else:
            assert (type in ORG_TYPES) or (type in NONRELATIONAL_TYPES)
    return [vertex_dict, edgelist]

if __name__ == '__main__':
    import ipdb as pdb
    import traceback
    import sys
    import signal
    signal.signal(signal.SIGUSR1, lambda _sig, _frame: pdb.set_trace())
    try:
        _vertex_dict, _edgelist = main()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
    with rasengan.tictoc('Pickling to ' + args.out_fn):
        with open(args.out_fn, 'wb') as f:
            pickle.dump([_vertex_dict, _edgelist], f, protocol=-1)
#  Local Variables:
#  eval: (linum-mode)
#  End:
