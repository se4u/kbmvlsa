SHELL := /bin/bash
.PHONY: tmp
.SECONDARY:
### English-Entities-Guidelines-V5.6.6.pdf
# The English portion of the ACE corpus comes from the following sources.
# | NW  | Newswire                       | Agence_France_English,AP,NYT,Xinhua_English
# | BN  | Broadcast_News                 | CNN,CNN_Headline
# | BC  | Broadcast_Conversation         | CNN_Crossfire,CNN_Inside_Politics,CNN_Late_Edition
# | WL  | Weblog                         | Internet_Blogs
# | UN  | Usenet_Newgroups               |
# | CTS | Conversational_Telephone_Speech| EARS_FISHER_2004
# ACE data is in [bc|bn|cts|nw|un|wl]/adj/*apf.xml and corresponding *sgm files.
# The apf files are written in UTF-8 format and they specify the sgm document
# that they are annotating as
# <source_file URI="CNN_LE_20030504.1200.01.sgm" SOURCE="broadcast conversation" TYPE="text" AUTHOR="LDC" ENCODING="UTF-8">
# Within each document there are multiple entities. Each entity has an id, type,
# subtype and a class
# | Id      | PER, ORG LOC, FAC, VEH, WEA
# | Subtype | PER.Individual, PER.group, PER.Indefinite
# | Class   | Negatively Quant, Specific Ref, Generic Ref, Under Specified Ref
# Each entity may be mentioned multiple times in different ways.
# The entity mentions have a type, extent and a head
# The mention types are either of
# | Names              | NAM | Proper nouns and nicknames, unquantifiable.               |
# | Quantified Nominal | NOM | Noun quantified with determiner, quantifier or possessive |
# | Bare Nominal       | BAR | An unquantified nominal construction                      |
# | Pronouns           | PRO | Pronouns but now wh-question words of 'that'              |
# | Wh-Question        | WHQ | Wh-question words and 'that'                              |
# | Headless           | HLS | The nominal head is not overtly extressed                 |
# | Partitive          | PTV | When we mention to a small part of the whole.             |
# ACE data is in [bc|bn|cts|nw|un|wl]/adj/*apf.xml and corresponding *sgm files.
ACE := $(HOME)/data/LDC2006T06/data/English

### The ACEtoWiki file contains the following columns
# link(s) | Document ID | Entity ID | Start position of mention's lexical head
# The LDC Entity Ids need to be mapped to the ACE entity Ids
# The links go directly to wikipedia.
# The Start position of mentions's lexical head uses the same offset scheme,
# which does not count the tags and calls the offset of first character 1.
ACEtoWIKI := $(HOME)/data/ACEtoWIKI_resource/ACEtoWIKI_resource.txt

default:
	echo "Specify Target"

data/mention_to_wikilist_filter_by_list_size_property_count: data/mention_to_wikilist_filter_by_list_size data/parsed_mentions
	./mention_to_wikilist_filter_by_list_size_property_count.py $+ # > $@

# ------------------------------------------------------- #
# Filter the input file of mentions to wikilists and keep #
# only lists that have at least N distinct mentions       #
# ------------------------------------------------------- #
data/mention_to_wikilist_filter_by_list_size: data/mention_to_wikilist
	./mention_to_wikilist_filter_by_list_size.py $< --thresh 10 # > $@

# --------------------------------------------------------------------- #
#  Look up the wikilist of the wikilink if its entity type, subtype are #
#  PER, Individual                                                      #
# --------------------------------------------------------------------- #
data/mention_to_wikilist: data/mention_and_type_to_wikilink
	./mention_to_wikilist.py $< \
	  --link_col 1 --entity_type_col 8 --entity_subtype_col 9 # > $@

# --------------------------------------------------------------- #
# Parse those sentences that contain mentions to Person entities. #
# The mention type does not matter. Just the entity type matters. #
# --------------------------------------------------------------- #
data/parsed_mentions: data/mention_and_type_to_wikilink
	./parse_mentions $< \
	  --link_col 1 --entity_type_col 8 --entity_subtype_col 9 \
	  --sentence_col 10 # > $@

# https://en.wikipedia.org/w/api.php?action=query&titles=John_Ashcroft&format=json&prop=categories&clshow=!hidden&cllimit=max

# ---------------------------------------------------------------------------- #
# TARGET: The target extends the ACEtoWIKI_resource. For each mention it adds  #
#   its entity type, entity subtype, entity class, mention id, type & sentence #
# Delimited by triple pipes                                                    #
# ---------------------------------------------------------------------------- #
data/mention_and_type_to_wikilink: $(ACEtoWIKI)
	./mention_and_type_to_wikilink.py # > $@
