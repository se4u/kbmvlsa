#!/usr/bin/env python
'''
| Filename    : basic_featurization_relational_bbn2.py
| Description : Basic Featurization of Relational BBN2.pkl
| Author      : Pushpendre Rastogi
| Created     : Sun Apr 17 22:10:30 2016 (-0400)
| Last-Updated: Sun Apr 17 23:06:39 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 21
'''
import os
import cPickle as pkl
import rasengan
import argparse
from entity import Entity
arg_parser = argparse.ArgumentParser(
    description='Do a basic featurization of the BBN2 data.')
arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
arg_parser.add_argument('--in_fn',
                        default="~/data/tackbp2015bbn2/relational_bbn2.pkl",
                        type=str)
arg_parser.add_argument('--out_fn',
                        default="~/data/tackbp2015bbn2/basicfeaturization_relational_bbn2.pkl",
                        type=str)
args = arg_parser.parse_args()
vertex_dict, edgelist = pkl.load(open(os.path.expanduser(args.in_fn)))
assert all(e.confidence == '"1.0"'
           for e in vertex_dict.itervalues())
# The total features
potential_feat = list(
    set(rasengan.flatten([e.keys()
                          for _ in vertex_dict.itervalues()
                          for e in _.featsets])))
STRING_FEAT = [e
               for e in potential_feat
               if e.endswith('~name')]
other_feat = ['~crime', '~time', '~document']

'''
print [e for e in potential_feat
 if e.endswith('~name')]

print [e for e in potential_feat
 if e.endswith('~type')]

print [e for e in potential_feat
 if e.endswith('~confidence')]

print [e for e in potential_feat
      if not e.endswith('~name')
      and not e.endswith('~type')
      and not e.endswith('~confidence')]
'''


def kpv(k, d, sep='~'):
    return k + sep + d[k]


def extract_feature_from_featset(fs):
    type = fs['type']
    value = fs['~confidence']
    try:
        l = [kpv('~document', fs)]
    except KeyError:
        l = []
    for k in STRING_FEAT:
        try:
            l.append(type + kpv(k, fs))
        except KeyError:
            pass
    return value, l


def str2float(s):
    return float(s.replace('"', ''))


PERFECT_HASH = dict((_e, idx)
                    for (idx, _e)
                    in enumerate(list(set(rasengan.flatten(rasengan.flatten(
                        [[extract_feature_from_featset(_)[1] for _ in e.featsets]
                         for e in vertex_dict.itervalues()]))))))
TOTAL_FEATURES = len(PERFECT_HASH)


def extract_feature_from_entity(v):
    val_feat = [extract_feature_from_featset(e) for e in v.featsets]
    features = []
    for val, feat in val_feat:
        value = str2float(val)
        for f in feat:
            features.append([PERFECT_HASH[f], value])
    return features


def main():
    new_dict = {}
    with rasengan.tictoc('Extracting Features'):
        for k in vertex_dict.keys():
            v = vertex_dict[k]
            new_dict[k] = Entity(v.guid,
                                 v.name,
                                 v.confidence,
                                 v.featsets,
                                 extract_feature_from_entity(v))

    with rasengan.tictoc('Pickling'):
        with open(os.path.expanduser(args.out_fn), 'wb') as f:
            pkl.dump(dict(vertex_dict=new_dict,
                          edgelist=edgelist,
                          TOTAL_FEATURES=TOTAL_FEATURES,
                          PERFECT_HASH=PERFECT_HASH),
                     f,
                     protocol=-1)

if __name__ == '__main__':
    main()
