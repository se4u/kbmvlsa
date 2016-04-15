#!/usr/bin/env python
'''
| Filename    : Entity.py
| Description : Entity Class
| Author      : Pushpendre Rastogi
| Created     : Fri Apr 15 00:52:53 2016 (-0400)
| Last-Updated: Fri Apr 15 01:04:50 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 2
'''


class Entity(object):
    __slots__ = ['guid', 'name', 'confidence', 'featsets']

    def __init__(self, guid, name, confidence):
        self.guid = guid
        self.name = name
        self.confidence = confidence
        self.featsets = []

    def append(self, val):
        self.featsets.append(val)
