#!/usr/bin/env python
'''
| Filename    : extract_leaf_relations_from_adept_ontology.py
| Description : Read the turtle specification of the ADEPT KB and print leaf relations.
| Author      : Pushpendre Rastogi
| Created     : Tue Mar  8 18:34:15 2016 (-0500)
| Last-Updated: Wed Mar  9 19:03:25 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 81
USAGE: ./extract_leaf_relations_from_adept_ontology.py |  sed 's#http://adept-kb.bbn.com/adept-core##g' | sort
'''
import config
import rdflib
from rdflib.namespace import Namespace
AB_Relation = rdflib.term.URIRef('http://adept-kb.bbn.com/adept-base#Relation')
AB_argument = rdflib.term.URIRef('http://adept-kb.bbn.com/adept-base#argument')
RDFNS_type = rdflib.term.URIRef(
    u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
OWL_Restriction = rdflib.term.URIRef(
    u'http://www.w3.org/2002/07/owl#Restriction')
OWL_onProperty = rdflib.term.URIRef(
    u'http://www.w3.org/2002/07/owl#onProperty')


def transitive_subjects(g, relation, start):
    l = []
    for r in (e[0] for e in g.triples((None, relation, start))):
        l.append(r)
        ll = transitive_subjects(g, relation, r)
        # import ipdb as pdb
        # pdb.set_trace()
        l.extend(ll)
    return l


def get_superclasses_of_node(g, r):
    return set([e[2] for e
                in g.triples((r, rdflib.namespace.RDFS.subClassOf, None))
                if not isinstance(e[2], rdflib.term.BNode)])


def get_immediate_property_restriction_on_node(g, r):
    tmp = set([e[2] for e
               in g.triples((r, rdflib.namespace.RDFS.subClassOf, None))
               if (isinstance(e[2], rdflib.term.BNode)
                   and len(list(g.triples((e[2],
                                           RDFNS_type,
                                           OWL_Restriction)))) > 0)])
    properties = []
    for pr in tmp:
        required_properties = [e[2]
                               for e
                               in g.triples((pr, OWL_onProperty, None))]
        assert len(required_properties) == 1
        properties.append(required_properties[0])
    return set(properties)


def get_all_property_restriction_on_node(g, r):
    imdt_pr = list(get_immediate_property_restriction_on_node(g, r))
    supcls = get_superclasses_of_node(g, r)
    for cls in supcls:
        cls_pr = list(get_all_property_restriction_on_node(g, cls))
        imdt_pr.extend(cls_pr)
    return set(imdt_pr)


def main():
    g = rdflib.Graph()

    # n3 is a superset of the turtle format.
    g.parse(args.adept_base_fn, format='n3')
    g.parse(args.adept_core_fn, format='n3')
    relation_list = list(g.transitive_subjects(
        rdflib.namespace.RDFS.subClassOf,
        AB_Relation))
    necessary_relations = set('''
    BeBorn BusinessEvent ChargeIndict  Die EmploymentMembership
    EndOrganization FamilyRelationship Founder
    InterpersonalRelationship InvestorShareholder JusticeEvent
    Leadership LifeEvent MemberOriginReligionEthnicity Membership
    OrganizationalAffiliation OrganizationWebsite
    OrgHeadquarter Origin ParentChildRelationship PartWhole
    PhysicalLocation Resident Role SiblingRelationship
    SpousalRelationship StartOrganization StudentAlum Subsidiary
    '''.strip().split())

    necessary_roles = set('''
    argument canonicalMention canonicalString thing timex2String
    xsdDate affiliatedEntity child crime defendant employeeMember
    entity founder investorShareholder leader location member
    organization parent person place role studentAlumni
    subOrganization time url'''.strip().split())

    necessary_things = set('Title URL Crime Person GeoPoliticalEntity '
                           'Organization'.strip().split())

    available_relations = set([str(e)[35:] for e in relation_list])
    print necessary_things
    assert (necessary_relations - available_relations) == set([])
    NON_LEAF_RELATIONS = []
    for r in (e for e
              in relation_list
              if str(e)[35:] in necessary_relations):
        sub_classes_of_r = list(g.triples(
            (None, rdflib.namespace.RDFS.subClassOf, r)))
        properties = [e for e in get_all_property_restriction_on_node(g, r)
                      if e != AB_argument]
        print ('NOT_LEAF'
               if len(sub_classes_of_r) > 0
               else 'YES_LEAF'),
        print len(properties), r, ' '.join(str(p) for p in properties)

if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('--seed', default=0, type=int, help='Default={0}')
    arg_parser.add_argument(
        '--adept_core_fn', default=config.adept_core_fn, type=str, help='Default={config.adept_core_fn}')
    arg_parser.add_argument(
        '--adept_base_fn', default=config.adept_base_fn, type=str, help='Default={config.adept_base_fn}')
    args = arg_parser.parse_args()
    # import random
    # random.seed(args.seed)
    # np.random.seed(args.seed)
    main()

exit(0)
'''
NOT_LEAF 0 core#OrganizationalAffiliation
NOT_LEAF 0 core#PartWhole
NOT_LEAF 1 core#FamilyRelationship core#person
NOT_LEAF 1 core#InterpersonalRelationship core#person
NOT_LEAF 1 core#PhysicalLocation core#location
NOT_LEAF 2 core#MemberOriginReligionEthnicity core#person core#affiliatedEntity
NOT_LEAF 2 core#Subsidiary core#parent core#subOrganization
NOT_LEAF 3 core#BusinessEvent core#time core#organization core#place
NOT_LEAF 3 core#JusticeEvent core#time core#crime core#place
NOT_LEAF 3 core#LifeEvent core#time core#person core#place

YES_LEAF 1 core#SiblingRelationship core#person
YES_LEAF 1 core#SpousalRelationship core#person

YES_LEAF 2 core#EmploymentMembership core#employeeMember core#organization
YES_LEAF 2 core#Founder core#founder core#organization
YES_LEAF 2 core#InvestorShareholder core#investorShareholder core#organization
YES_LEAF 2 core#Leadership core#leader core#affiliatedEntity
YES_LEAF 2 core#OrgHeadquarter core#organization core#location
YES_LEAF 2 core#OrganizationWebsite core#url core#organization
YES_LEAF 2 core#Origin core#person core#affiliatedEntity
YES_LEAF 2 core#Resident core#person core#location
YES_LEAF 2 core#Role core#role core#person
YES_LEAF 2 core#StudentAlum core#organization core#studentAlumni
YES_LEAF 3 core#BeBorn core#time core#person core#place
YES_LEAF 3 core#EndOrganization core#time core#organization core#place
YES_LEAF 3 core#ParentChildRelationship core#parent core#child core#person
YES_LEAF 4 core#Membership core#parent core#member core#organization core#subOrganization
YES_LEAF 4 core#StartOrganization core#agent core#time core#organization core#place
YES_LEAF 6 core#ChargeIndict core#time core#defendant core#crime core#prosecutor core#adjudicator core#place
YES_LEAF 6 core#Die core#victim core#time core#agent core#person core#instrument core#place
'''
