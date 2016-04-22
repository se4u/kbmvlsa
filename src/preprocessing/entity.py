#!/usr/bin/env python
'''
| Filename    : Entity.py
| Description : Entity Class
| Author      : Pushpendre Rastogi
| Created     : Fri Apr 15 00:52:53 2016 (-0400)
| Last-Updated: Sun Apr 17 22:52:00 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 5
'''


class Entity(object):
    __slots__ = ['guid', 'name', 'confidence', 'featsets', 'features']

    def __init__(self, guid, name, confidence, featsets=None, features=None):
        self.guid = guid
        self.name = name
        self.confidence = confidence
        self.featsets = [] if featsets is None else featsets
        self.features = [] if features is None else features

    def append(self, val):
        self.featsets.append(val)
