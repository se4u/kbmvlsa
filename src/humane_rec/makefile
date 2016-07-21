SHELL := /bin/bash
.PHONY:
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
ACE1 := $(HOME)/data/LDC2006T06/data/English
# proc = adj and fp2 won't work.
proc := timex2norm
ACE := $(ACE1).$(proc).sgm_apf
### The ACEtoWiki file contains the following columns
# link(s) | Document ID | Entity ID | Start position of mention's lexical head
# The LDC Entity Ids need to be mapped to the ACE entity Ids
# The links go directly to wikipedia.
# The Start position of mentions's lexical head uses the same offset scheme,
# which does not count the tags and calls the offset of first character 1.
ACEtoWIKI := $(HOME)/data/ACEtoWIKI_resource/ACEtoWIKI_resource.txt

default:
	echo "Specify Target"

echo_%:
	echo $($*)

data/wiki_link_individual_mentions.pkl: data/wiki_link
	./extract_person_mentions_from_wikilink_data.py \
	  --thrift_class_dir $< \
	  --thrift_data_dir /export/b15/prastog3/wikilinks \
	  --out_fn $@

data/wiki_link: data/wiki-link-v0.1.thrift
	thrift -gen py:new_style $< ; mv gen-py $@

data/mention_to_wikilist_filter_by_list_size_property_count: data/mention_to_wikilist_filter_by_list_size data/parsed_mentions
	./mention_to_wikilist_filter_by_list_size_property_count.py $+ # > $@


# After getting the freebase id, filter these ids out from the cluweb data that
# Xuchen had. There are 13217 files and 100 files take 23 seconds and creates
# 145k lines with 43M data. A single thread will finish in one hour and create
# 6 GB data.
CLUDIR := /export/common/data/processed/clueweb09-freebase-annotation/extractedAnnotation
data/cluweb_freebase_mentions_of_mids: data/list_of_mid_to_extract
	find $(CLUDIR) -name *.gz | xargs -I % zgrep -F -f data/list_of_mid_to_extract % > $@

data/list_of_mid_to_extract: data/unique_human_entities_in_freebase
	awk '{print $$2}' $< > $@

data/unique_human_entities_in_freebase: data/unique_human_entities_wikidata_id
	grep -v NOT_IN_FREEBASE $< > $@

# 123 people are not in freebase.
# But only 72 of those ar real. the rest 51 are just crappy names.
# grep -v name data/unique_human_entities_not_in_freebase
# These include people like:
# http://en.wikipedia.org/wiki/Heidi_Collins NOT_IN_FREEBASE
# http://en.wikipedia.org/wiki/Martin_Savidge NOT_IN_FREEBASE
# http://en.wikipedia.org/wiki/Mark_Alan_Wilson NOT_IN_FREEBASE
# http://en.wikipedia.org/wiki/A._Alfred_Taubman NOT_IN_FREEBASE
# http://en.wikipedia.org/wiki/Leslie_L._Byrne NOT_IN_FREEBASE
# http://en.wikipedia.org/wiki/Edward_H._Brooks NOT_IN_FREEBASE
data/unique_human_entities_not_in_freebase: data/unique_human_entities_wikidata_id
	grep NOT_IN_FREEBASE $< > $@

data/unique_human_entities_wikidata_id: data/unique_human_entities
	./unique_human_entities_wikidata_id.py \
	  --human_entity_url_fn $< \
	  --wikidata_to_freebase_id_fn ~/data/freebase_to_wikidata/freebase_to_wikidata.compressed \
	  --shelf_fn data/unique_human_entities_wikidata_id.cache \
	  --out_fn $@

data/unique_human_entities: data/category_to_entities
	cat $</* | sort -u > $@

data/category_to_entities: data/category_to_data
	-mkdir $@; \
	for f in `\ls -b $<`; do awk '{print $$1}' $</$$f | sort -u > $@/$$f ; done

# The categories were generated using
# hn 54 data/analyze_categories_of_individuals.txt | tn 53 | awk -F'"' '{printf "\"%s\" ", $2}'
data/category_to_data:
	for f in "21st-century American writers" "American people of Irish descent" "20th-century American writers" "American Roman Catholics" "American male writers" "American political writers" "20th-century American politicians" "Presidential Medal of Freedom recipients" "21st-century American politicians" "Democratic Party United States Senators" "CNN people" "Given names" "1946 births" "American people of English descent" "American memoirists" "Democratic Party members of the United States House of Representatives" "American television reporters and correspondents" "American Jews" "Recipients of the Bronze Star Medal" "American military personnel of the Vietnam War" "American male film actors" "Presidents of the United States" "1943 births" "English masculine given names" "1942 births" "American people of Scottish descent" "American Presbyterians" "Republican Party members of the United States House of Representatives" "1954 births" "George W. Bush Administration cabinet members" "1953 births" "2004 deaths" "American women writers" "1944 births" "Republican Party state governors of the United States" "Democratic Party (United States) presidential nominees" "Grammy Award winners" "1947 births" "American people of German descent" "New York Democrats" "20th-century women writers" "20th-century American businesspeople" "American anti-communists" "United States presidential candidates, 2008" "20th-century American male actors" "United States Army soldiers" "21st-century women writers" "1948 births" "United States presidential candidates, 2004" "Recipients of the Order of the Cross of Terra Mariana, 1st Class" "1945 births" "Recipients of the Purple Heart medal" "New York Republicans" ; do \
	 echo $$f;  ./category_to_data.sh $@ "$$f" | sort -u ; \
	done; touch $@

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
data/parsed_mentions: data/mention_and_type_for_individuals
	./parse_mentions.py --d1 ' |||' \
	  --begin_mention_col 5 \
	  --end_mention_col 6 \
	  --sentence_col 7 \
	  --in_fn $< --out_fn $@

# -------------------------------------- #
# Analyze the categories of individuals. #
# cat_col is indexed from 0              #
# -------------------------------------- #
data/analyze_categories_of_individuals.txt: data/mention_and_type_for_individuals
	./analyze_categories_of_individuals.txt.py \
	  --d1 ' |||' --d2 ';' --cat_col 9 --link_col 8 --link_count_thresh 5 \
	  --in_fn $< --link_to_count_fn data/counts_of_mentions_of_individuals.txt > $@

# -------------------------------------------- #
# Count the number of mentions of individuals. #
# -------------------------------------------- #
data/counts_of_mentions_of_individuals.txt: data/mention_and_type_for_individuals
	./counts_of_mentions_of_individuals.txt.sh $< > $@

# --------------------------------------------- #
# Filter the mentions down to only individuals. #
# --------------------------------------------- #
data/mention_and_type_for_individuals: data/mention_and_type_to_wikilink
	./mention_and_type_for_individuals.sh $< > $@

# ---------------------------------------------------------------------------- #
# TARGET: The target extends the ACEtoWIKI_resource. For each mention it adds  #
# its entity type, entity subtype, entity class, mention id, type, sentence,   #
# wikilink and wiki categories delimited by triple pipes.                      #
# ---------------------------------------------------------------------------- #
data/mention_and_type_to_wikilink: data/ace_document_to_sentence.pkl # data/wikilink_category.pkl
	./mention_and_type_to_wikilink.py \
	 --wikilink_category_pkl_fn data/wikilink_category.pkl \
	 --document_to_sentence_pkl_fn $< \
	 --out_file $@

# --------------------------------------- #
# Map from document to list of sentences. #
# --------------------------------------- #
data/ace_document_to_sentence.pkl: ace_document_to_sentence.pkl.py
	./ace_document_to_sentence.pkl.py $@

# ------------------------------------ #
# Map from wikilink to wiki categories #
# The name of file becomes the key and #
# the contents of file become value    #
# ------------------------------------ #
data/wikilink_category.pkl: data/wikilink_category_cache
	./wikilink_category.pkl.py $< $@

# -------------------------------------------------------------------- #
# This step uses jq to extract categories from json and renames files. #
# The usage of jq in a loop makes this step slow                       #
# -------------------------------------------------------------------- #
data/wikilink_category_cache: data/wikilink_category_cache.raw
	./wikilink_category_cache.sh $< $@

# -------------------------------------------------------- #
# Download raw json from wikipedia in a single connection. #
# -------------------------------------------------------- #
data/wikilink_category_cache.raw: data/wikilink_url
	-mkdir $@; cd $@; wget -i ../../$<

data/wikilink_url_hash_revision: data/wikilink_url
	grep '%23' $< > $@

# Note that "#" and unicode characters need to be decoded.
# such as ñ
data/wikilink_url: data/wikilinks
	awk '{printf("https://en.wikipedia.org/w/api.php?action=query&titles=%s&format=json&prop=categories&clshow=!hidden&cllimit=max&redirects\n", $$1)}' $< > $@

data/wikilinks: $(ACEtoWIKI)
	awk -F'\t' '{print $$1}' $< | sort -u | \
	  grep -v -E '(MISSING SENSE|NO PAGE|NO_ANNOTATION)' | \
	  sed  's#http://en.wikipedia.org/wiki/##g; s.#.%23.g' | \
	  tr ' ' '\n' | sort -u > $@

$(ACE): $(ACE1)
	-mkdir $@; \
	for d in bc bn cts nw un wl; do \
	  cp $(ACE1)/$$d/$(proc)/*apf.xml $(ACE)/ ; \
	  cp $(ACE1)/$$d/$(proc)/*sgm $(ACE)/ ; \
	done ; \
	chmod 444 $(ACE)/*
