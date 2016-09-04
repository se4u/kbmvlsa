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


demo:
	./demonstrate_similarity_idea.py

CLSP_DIR := /home/prastog3/projects/kbvn/src/humane_rec

demo_emb:
	./demonstrate_similarity_idea.emb.py

# --------------------------------------------------- #
# I need to tunnel from local -> clsp -> test1 -> r6n #
# --------------------------------------------------- #

curl_call: # tunnel
	./curl_call.sh "Carly Fiorina, former CEO of Hewlett Packard, told the assembled troops Carly Fiorina, former CEO of Hewlett Packard, told the assembled troops."

tunnel:
	./multi_hop_tnl.sh prastog3@login.clsp.jhu.edu prastogi@test1.hltcoe.jhu.edu prastogi@r6n23

# After getting the freebase id, filter these ids out from the cluweb data that
# Xuchen had. There are 13217 files and 100 files take 23 seconds and creates
# 145k lines with 43M data. A single thread will finish in one hour and create
# 6 GB data.
# md5sum data/cluweb_freebase_mentions_of_mids
# fd1c29bbd17c5f9e993833cc3e826602 *data/cluweb_freebase_mentions_of_mids
# This file is also backed up at
# /export/projects/prastogi/kbvn/cluweb_freebase_mentions_of_mids
CLUDIR := /export/common/data/processed/clueweb09-freebase-annotation/extractedAnnotation
data/cluweb_freebase_mentions_of_mids: data/list_of_mid_to_extract
	find $(CLUDIR) -name *.gz | xargs -I % zgrep -F -f data/list_of_mid_to_extract % > $@

data/list_of_mid_to_extract: data/unique_human_entities_in_freebase
	awk '{print $$2}' $< > $@

data/unique_human_entities_in_freebase: data/unique_human_entities_wikidata_id
	grep -v NOT_IN_FREEBASE $< > $@

# 123 people are not in freebase.
# But only 72 of those ar real. Rest 51 are names of things, not actual things.
# grep -v name data/unique_human_entities_not_in_freebase
# These include people like:
# http://en.wikipedia.org/wiki/Heidi_Collins NOT_IN_FREEBASE
# http://en.wikipedia.org/wiki/Martin_Savidge NOT_IN_FREEBASE
# http://en.wikipedia.org/wiki/Leslie_L._Byrne NOT_IN_FREEBASE
data/unique_human_entities_not_in_freebase: data/unique_human_entities_wikidata_id
	grep NOT_IN_FREEBASE $< > $@

data/unique_human_entities_wikidata_id: data/unique_human_entities
	./unique_human_entities_wikidata_id.py \
	  --human_entity_url_fn $< \
	  --wikidata_to_freebase_id_fn ~/data/freebase_to_wikidata/freebase_to_wikidata.compressed \
	  --shelf_fn data/unique_human_entities_wikidata_id.cache \
	  --out_fn $@

# -------------------------------------------------------------------------- #
# ######################## EXPERIMENTS SECTION ############################# #
# -------------------------------------------------------------------------- #
EXPERIMENT_CATEGORY_LIST := data/list_of_categories_for_wikilink_experiments.txt
# ------------------------------------------- #
# CONSTANT                 MEAN RANK: 145.13  #
# COUNT                    MEAN RANK: 170.57  #
# LOG_COUNT                MEAN RANK: 161.50  #
# SQRT_COUNT               MEAN RANK: 172.83  #
# FREQ                     MEAN RANK: 181.41  #
# SQ_FREQ                  MEAN RANK: 208.54  #
# SQRT_FREQ                MEAN RANK: 136.40  #
# GM_SQRT_FREQ_SQRT_COUNT  MEAN RANK: 141.50  #
# --------------------------------------------#
# By intervening I can get a jump in the ranks.
rank_according_to_modes:
	for f in CONSTANT COUNT LOG_COUNT SQRT_COUNT FREQ SQ_FREQ SQRT_FREQ GM_SQRT_FREQ_SQRT_COUNT ; \
	do \
	  echo; \
	  echo $$f; \
	  ./rank_according_to_modes.py --intervene_modes 1 --cnt_transform $$f > data/rank_according_to_modes.$${f}.intervene~1.txt; \
	  ./rank_according_to_modes.py --intervene_modes 0 --cnt_transform $$f > data/rank_according_to_modes.$${f}.intervene~0.txt; \
	done

data/rank_according_to_modes.txt:
	./rank_according_to_modes.py > $@

show_data_for_categories: data/list_of_wiki_link_entities
	for f in $$( cat $(EXPERIMENT_CATEGORY_LIST)   ); do \
	  echo $$( join $< data/category_to_entities/$$f | wc -l) data/category_to_entities/$$f;\
	done | sort -k 1 -n -r \
	| tee /dev/fd/2 \
	| awk 'BEGIN{a=0;b=0}{a=a+$$1; b=b+1}END{print a, b}'

data/list_of_wiki_link_entities: data/wiki_link_individual_mentions.pkl
	python -c 'from __future__ import print_function; import cPickle as p; [print(k) for k in p.load(open("$<"))]' | sort > $@

# Experiment 1 : Based on the descriptors for all the entities in
# the categories, infer the commonalities between these people.

# Experiment 2 : Rank the commonalities inferred either automatically
# or manually to then rank the remaining entities.



# -------------------------------------------------------------- #
# - Don't Do BOW / Linguistic methods
#    - may not need discriminative feature selection.
#    - then add discriminative feature selection.
# - Do BOW features
#    - feature selection by picking feature that are most
#    - discriminative between random entities and the entities
#    - that were given to me
# -------------------------------------------------------------- #
# for f in eddd3 4b43 0967 5d65 7a65 a295 e854 27b2 ec22 42ca; do \
#   echo; echo ${f}*.mode_5; \
#   grep -E 'mode_idx= [0-9]* initial' ${f}* \
#      | sed 's#http://en.wikipedia.org/wiki/##g' \
#      | sed 's# [A-Za-z,_().-]*:##g' \
#      | cut -d ' ' -f 10- ; \
#   echo ${f}*.baseline; \
#   cat ${f}*baseline; \
# done
my_mode_%:
	for f in eddd3 4b43 0967 5d65 7a65 a295 e854 27b2 ec22 42ca; do \
	  a=$$(\ls data/random/details/$$f*); \
	  cn=$${a#*\.}; \
	  time ./demonstrate_similarity_idea.py \
	    --emb_pkl_fn /Users/pushpendrerastogi/data/embedding/mvlsa/combined_embedding_0.emb.pkl \
	    --ent_file data/category_to_entities/$$cn \
	    --feat_file $$a \
	    --mode_count $* \
	  > data/random/results/$$f.mode_$* ; \
	done

bupper:
	for f in eddd3 4b43 0967 5d65 7a65 a295 e854 27b2 ec22 42ca; do \
	  bash -i -c "printf 'Total categories'; wc -l data/random/$$f*; cat data/random/$$f* | sed -E 's#^ *##g;s#:[0-9]*##g;' | common_terms | head -10" > data/random/results/$$f.$@ ; \
	done

baseline:
	for f in eddd3 4b43 0967 5d65 7a65 a295 e854 27b2 ec22 42ca; do \
	  bash -i -c "printf 'Total categories'; wc -l data/random/$$f*; cat data/random/$$f* | lower | sed -E 's#^ *##g;s#:[0-9]*##g;' | common_terms | head -10" > data/random/results/$$f.$@ ; \
	done

get_stats_%: data/entity_descriptors_procoref~%.psv
	source $(HOME)/.bashrc ;\
	wc -l $< ;\
	cat $< | awk '{printf "%d\n", NF-2; }' | maxRowByColumn ;\
	cat $< | awk '{printf "%d\n", NF-2; }' | sumColumns ;\
	cat $< \
	 | awk '{printf "%d\n", NF-2; }'  \
	 | python -c 'import sys; from numpy import histogram as h; (a,b) = h([int(_.strip()) for _ in list(sys.stdin)], [0, 5, 25, 125, 625, 3250]); print zip(zip(b[0:], b[1:]), a)'

# The final step to extracting the governing tokens from sentences.
data/entity_descriptors_procoref~%.psv: data/wikimic_identify_governors_procoref~%.spkl
	./entity_descriptors_procoref.py $< > $@

data/entity_descriptors_procoref~%~noaux.psv: data/wikimic_identify_governors_procoref~%.spkl
	./entity_descriptors_procoref.py $< --remove_auxiliary_verb 1 > $@

# Compute the fixed point of a set of rules for extracting governors.
data/wikimic_identify_governors_procoref~%.spkl: data/wikimic_create_entity_token_set_procoref~%.spkl
	./wikimic_identify_governors.py --in_fn $< --out_fn $@ --debug_print 0

# -------------------------------------------------------------- #
# ETS includes the coreference entities.                         #
# We have now included the coreferent tokens including pronouns. #
# -------------------------------------------------------------- #
# data/wikimic_create_entity_token_set_1.spkl
# data/wikimic_create_entity_token_set_1.spkl
data/wikimic_create_entity_token_set_procoref~%.spkl: data/wikimic_tokenize_parse_sentence.spkl
	./wikimic_create_entity_token_set.py \
	  --in_fn $< --out_fn $@ \
	  --pronomial_coref $*

# --------------------------------------------------------------------------- #
# Unfortunately, the easiest way to parse and tokenize involves transferring  #
# the sentences to the mini grid. Which means I need to write each sentence to#
# a line and then I need to gzip it. then copy it over 3 hops to r6n24.       #
# Then on r6n24 I will run a command to parse this data and store to a file.  #
# Then I will copy the data back and store into a pickle.                     #
# --------------------------------------------------------------------------- #
# At this point the file is big enough that it makes sense to switch to
# `streaming-pkl`, and load the dict, one key at a time.
data/%.spkl: data/%.pkl
	./create_spkl.py --in_fn $< --out_fn $@

data/wikimic_tokenize_parse_sentence.pkl: data/wikimic_tokenize_parse_sentence.conll.gz data/wikimic_extract_sentence_boundary.txt.gz data/wikimic_extract_sentence_boundary.pkl
	./wikimic_tokenize_parse_sentence.py \
	  --in_parse_gz $< \
	  --in_sent_gz $(word 2,$+) \
	  --in_fn $(word 3,$+) \
	  --out_fn $@

data/wikimic_tokenize_parse_sentence.conll.gz:
	ssh prastog3@login.clsp.jhu.edu "rsync --progress -av -e ' ssh -A -t prastogi@test1.hltcoe.jhu.edu ssh -A -t prastogi@r6n24 ' :/home/hltcoe/prastogi/$(notdir $@) /home/prastog3/ "
	scp prastog3@login.clsp.jhu.edu:/home/prastog3/$(notdir $@) $(dir $@)

parse_on_r6n24: # Do not run docker in tty mode.
	zcat wikimic_extract_sentence_boundary.txt.gz \
	  | docker run -i syntaxnet-parser 2> /dev/null \
	  | gzip -9 > wikimic_tokenize_parse_sentence.conll.gz

copy_to_r6n24: data/wikimic_extract_sentence_boundary.txt.gz
	scp $< prastog3@login.clsp.jhu.edu:/home/prastog3/
	ssh prastog3@login.clsp.jhu.edu "rsync --progress -av -e ' ssh -A -t prastogi@test1.hltcoe.jhu.edu ssh -A -t prastogi@r6n24 ' /home/prastog3/$(notdir $<) :/home/hltcoe/prastogi/ "

data/wikimic_extract_sentence_boundary.txt.gz: data/wikimic_extract_sentence_boundary.pkl
	python -c 'from __future__ import print_function; from cPickle import load; data = load(open("$<")); [print(s) for k in data for m in data[k] for s in m["sentences"]]' | gzip -9 > $@

# There are 371 entities, each with 127642 sentences about them.
# I want to parse these sentences as quickly and as good as possible.
# For the kind of descriptions that I want to draw, extra accuracy may not
# be necessary, but still it will be nice to be able to use PMP parses.
# In 35 minutes, it parsed 44776 sentence,
# In 110 minutes we parsed 156,652 sentences.
# We have 415397 sentences, total time is 5 hours.
data/wikimic_extract_sentence_boundary.pkl: data/wikimic_remove_translate_nonascii.pkl
	./wikimic_extract_sentence_boundary.py --in_fn $< --out_fn $@

data/wikimic_remove_translate_nonascii.pkl: data/wiki_link_individual_mentions.pkl
	./wikimic_remove_translate_nonascii.py --in_fn $< --out_fn $@

# ----------------------- WIKILINKS DATA PROCESSING ----------------------- #
# Extract entity mentions from wiki link corpus that contains real mentions #
# of entities in the form of links from web pages to wikipedia articles.    #
# Data is stored as thrift communications. The pkl files contains a map     #
# from entities in the `human_entity_fn` to a list of mentions stored in    #
# the `thrift_data_dir`. The data in `thrift_data_dir` has to be read using #
# the classes in `thrift_class_dir`                                         #
# ------------------------------------------------------------------------- #
# USAGE: See wiki_link_individual_mentions.ipynb
# Basically it contains all the facts in the wikilinks data about `371`
data/wiki_link_individual_mentions.pkl: data/wiki_link /export/b15/prastog3/wikilinks
	./extract_person_mentions_from_wikilink_data.py \
	  --thrift_class_dir $< \
	  --thrift_data_dir $(word 2,$+) \
	  --out_fn $@ # --human_entity are  HARDCODED in file.

data/chosen_url_%_mthresh~10: data/wikilink_category_to_url_and_count_reverse_index.pkl data/chosen_wikilink_categories_%_mthresh~10
	./chosen_url.py --caturl_pkl $< --chosen_cat $(word 2,$+) --mention_thresh 10 > $@
	echo $@ ; cut -d' ' -f 2 $@  | sort -u | wc -l

# -------------------------------------------------------------------- #
# Based on the counts of the wikilink categories, pick a few good ones #
# The basic principle is that I want to chose middle of the road       #
# categories that are neither dominated by a single entity. nor are    #
# too voluminous, neither are they too small                           #
# -------------------------------------------------------------------- #
# for n in 100 1000 1500 2000; do m data/chosen_wikilink_categories_${n}_mthresh~10; done
# I don't want any of the
data/chosen_wikilink_categories_%_mthresh~10: data/wikilink_category_to_count_n_ratio_10.tsv
	awk '{if($$2 >= 10 && $$2 <= 300 && $$4 >= 5 && $$4 <= 50 && match($$1, "[0-9]") == 0){print $$0}}' $<  \
	| sort -k 4 -r -n \
	| if [[ $* == all ]] ; then tee ; else pyshuf --N $* --seed 1234 ; fi > $@

data/wikilink_category_to_count_n_ratio_%.tsv: data/wikilink_category_to_count_%.tsv
	awk '{print $$1, $$2, $$3, ($$2==0)?0:int($$3/$$2)}' $<  > $@
# ------------------------------------------------------------- #
# Create a reverse index of Categories to Urls and their Counts #
# ------------------------------------------------------------- #
rsync_2:
	for f in data/wikilink_category_to_count.tsv \
                 data/wikilink_category_to_url_and_count_reverse_index.pkl \
	         wikilink_category_to_url_and_count_reverse_index.py; do\
	  rsync -vz prastog3@b15:~/projects/kbvn/src/humane_rec/$$f ./$$f ; done

data/wikilink_category_to_count_%.tsv: data/wikilink_category_to_url_and_count_reverse_index.pkl
	./wikilink_category_to_count.py --mention_thresh $* --in_pkl_fn $< --out_fn $@

data/wikilink_category_to_url_and_count_reverse_index.pkl: data/dbpedia_cat_index.pkl data/wikilink_dbpedia_categories.pkl data/dbpedia_people.list
	./wikilink_category_to_url_and_count_reverse_index.py \
	 --ci_pkl_fn $< \
	 --wdc_pkl_fn $(word 2,$+) \
	 --out_pkl_fn $@ \
	 --out_tsv_fn data/wikilink_category_to_count.tsv \
	 --admissible_url_fn $(word 3,$+)

# --------------------------------------------------------------------------- #
# Compile a list of URLs that we know to be of the person type using dbpedia. #
# --------------------------------------------------------------------------- #
data/dbpedia_people.list: data/dbpedia_person.classes
	bzcat $(HOME)/data/dbpedia/instance_types_en.ttl.bz2  \
	 | fgrep -f $< \
	 | cut -d' ' -f 1 \
	 | python -c 'from __future__ import print_function; import sys; [print(e.strip()[29:-1]) for e in sys.stdin]' > $@

# --------------------------------------------------------------------- #
# Find the categories of the URLs in Wikilinks by looking up in DBPedia #
# --------------------------------------------------------------------- #
rsync_1:
	for f in dbpedia_cat_index.pkl wikilink_dbpedia_categories.pkl; do\
	  rsync -vz prastog3@b15:~/projects/kbvn/src/humane_rec/data/$$f data/ ; done

# Executed on CLSP because it needs high memory.
# dbpedia_cat_index maps categories to their numerical id.
# wikilink_dbpedia_categories maps urls to their categories and counts.
data/dbpedia_cat_index.pkl data/wikilink_dbpedia_categories.pkl: data/wiki_link_url_counts.pkl ~/Downloads/dbpedia
	./wikilink_dbpedia_categories.py

# ------------------------------------------------------------------------------- #
# Count the number of times a wikipedia url is mentioned in the wikilinks dataset #
# ------------------------------------------------------------------------------- #
data/wiki_link_url_counts.pkl: data/wiki_link /export/b15/prastog3/wikilinks
	./count_mentions_from_wikilink_data.py
	  --thrift_class_dir $< \
	  --thrift_data_dir $(word 2,$+) \
	  --out_fn $@

# ------------------------------------------------------------------------- #
# Create thrift classes to read the wikilinks dataset that was released by  #
# Sameer Singh et. al. This dataset was created by mining web links         #
# pointing to Wikipedia pages.                                              #
# ------------------------------------------------------------------------- #
data/wiki_link: data/wiki-link-v0.1.thrift
	thrift -gen py:new_style $< ; mv gen-py $@

# ------------------------------------------------------------------------ #
# A single list of human entities that were present in the ACE 2005 Corpus #
# ------------------------------------------------------------------------ #
data/unique_human_entities: data/category_to_entities
	cat $</* | sort -u > $@

# ----------------------------------------------------------------- #
# Create list of wiki entities that fall in a category acc. to wiki #
# The list is not exhaustive, it only contains entities that were   #
# well populated within the ACE 2005 corpus.                        #
# ----------------------------------------------------------------- #
data/category_to_entities: data/category_to_data
	-mkdir $@; \
	for f in `\ls -b $<`; do awk '{print $$1}' $</$$f | sort -u > $@/$$f ; done

# ----------------------------------------------------------------------- #
# The category to data files contain data from the ACE 2005 corpus about  #
# mention of entities that are in `mention_and_type_for_individuals` file #
# ----------------------------------------------------------------------- #
# The categories were generated using
# hn 54 data/analyze_categories_of_individuals.txt | tn 53 | awk -F'"' '{printf "\"%s\" ", $2}'
data/category_to_data: data/parsed_mentions
	for f in "21st-century American writers" "American people of Irish descent" "20th-century American writers" "American Roman Catholics" "American male writers" "American political writers" "20th-century American politicians" "Presidential Medal of Freedom recipients" "21st-century American politicians" "Democratic Party United States Senators" "CNN people" "Given names" "1946 births" "American people of English descent" "American memoirists" "Democratic Party members of the United States House of Representatives" "American television reporters and correspondents" "American Jews" "Recipients of the Bronze Star Medal" "American military personnel of the Vietnam War" "American male film actors" "Presidents of the United States" "1943 births" "English masculine given names" "1942 births" "American people of Scottish descent" "American Presbyterians" "Republican Party members of the United States House of Representatives" "1954 births" "George W. Bush Administration cabinet members" "1953 births" "2004 deaths" "American women writers" "1944 births" "Republican Party state governors of the United States" "Democratic Party (United States) presidential nominees" "Grammy Award winners" "1947 births" "American people of German descent" "New York Democrats" "20th-century women writers" "20th-century American businesspeople" "American anti-communists" "United States presidential candidates, 2008" "20th-century American male actors" "United States Army soldiers" "21st-century women writers" "1948 births" "United States presidential candidates, 2004" "Recipients of the Order of the Cross of Terra Mariana, 1st Class" "1945 births" "Recipients of the Purple Heart medal" "New York Republicans" ; do \
	 echo $$f;  ./category_to_data.sh $@ "$$f" | sort -u ; \
	done; touch $@

# ------------------------------------------------------- #
# Filter the input file of mentions to wikilists and keep #
# only lists that have at least N distinct mentions       #
# ------------------------------------------------------- #
data/mention_to_wikilist_filter_by_list_size_property_count: data/mention_to_wikilist_filter_by_list_size data/parsed_mentions
	./mention_to_wikilist_filter_by_list_size_property_count.py $+ # > $@

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

# ----------------------------------------- #
# Create URL's from wikipedia page headers. #
# ----------------------------------------- #
data/wikilink_url: data/wikilinks
	awk '{printf("https://en.wikipedia.org/w/api.php?action=query&titles=%s&format=json&prop=categories&clshow=!hidden&cllimit=max&redirects\n", $$1)}' $< | \
	  python3 -c 'import sys, rasengan; [print(rasengan.wiki_encode_url(url.strip())) for url in sys.stdin]' > $@

# -------------------------------------------------------------------------- #
# Extract header of links to Wikipedia of all entries in the ACE 2005 corpus #
# -------------------------------------------------------------------------- #
data/wikilinks: $(ACEtoWIKI)
	awk -F'\t' '{print $$1}' $< | sort -u | \
	  grep -v -E '(MISSING SENSE|NO PAGE|NO_ANNOTATION)' | \
	  sed  's#http://en.wikipedia.org/wiki/##g; s.#.%23.g' | \
	  tr ' ' '\n' | sort -u > $@

# ---------------------------------------------------------------------- #
# Prepare the ACE 2005 Corpus by adding its files to a single directory. #
# ---------------------------------------------------------------------- #
$(ACE): $(ACE1)
	-mkdir $@; \
	for d in bc bn cts nw un wl; do \
	  cp $(ACE1)/$$d/$(proc)/*apf.xml $(ACE)/ ; \
	  cp $(ACE1)/$$d/$(proc)/*sgm $(ACE)/ ; \
	done ; \
	chmod 444 $(ACE)/*
