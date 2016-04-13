#!/usr/bin/env python
'''
| Filename    : type_lattice_max_select.py
| Description : Given a list of tuples on stdin select the leaf type for each entity.
| Author      : Pushpendre Rastogi
| Created     : Tue Apr 12 17:20:33 2016 (-0400)
| Last-Updated: Wed Apr 13 19:00:36 2016 (-0400)
|           By: Pushpendre Rastogi
|     Update #: 31
'''
import sys
hierarchy = '''
adept-base#PredicateArgument
	adept-base#Relation
		adept-core#PhysicalLocation
			adept-core#OrgHeadquarter
			adept-core#Resident
		adept-core#OrganizationWebsite
		adept-core#InterpersonalRelationship
			adept-core#FamilyRelationship
				adept-core#SpousalRelationship
				adept-core#ParentChildRelationship
				adept-core#SiblingRelationship
			adept-core#Role
		adept-core#PartWhole
			adept-core#Subsidiary
			adept-core#Membership
		adept-core#OrganizationalAffiliation
			adept-core#EmploymentMembership
			adept-core#StudentAlum
			adept-core#Leadership
			adept-core#Founder
			adept-core#InvestorShareholder
		adept-core#MemberOriginReligionEthnicity
			adept-core#Origin
		adept-base#Event
			adept-core#LifeEvent
				adept-core#BeBorn
				adept-core#Die
			adept-core#JusticeEvent
				adept-core#ChargeIndict
			adept-core#BusinessEvent
				adept-core#EndOrganization
				adept-core#StartOrganization
	adept-base#Thing
		adept-base#Date
		adept-base#Entity
			adept-core#GeoPoliticalEntity
			adept-core#Organization
			adept-core#Organization
				adept-core#GeoPoliticalEntity
			adept-core#Person
		adept-base#GenericThing
			adept-core#Crime
			adept-core#Title
			adept-core#URL
'''.strip()

pc = None
path = []
path_sets = []
path_leaf = []
for e, c in [(e.strip(), e.count('\t')) for e in hierarchy.split('\n')]:
    if pc is not None and c <= pc:
        path_sets.append(set(path))
        path_leaf.append(path[-1])
        # Delete 1 if pc - c == 0
        # Delete 2 if pc - c == 1
        del path[-(pc - c + 1):]
    path.append(e)
    pc = c
path_sets.append(set(path))
path_leaf.append(path[-1])

pkey = None
types = []
for row in sys.stdin:
    ckey, ctype = row.strip().split()
    if pkey is not None and ckey != pkey:
        assert set(types) in path_sets
        print pkey, path_leaf[path_sets.index(set(types))]
        types = []
        pkey = None
    pkey = ckey
    types.append(ctype)
