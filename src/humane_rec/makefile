SHELL := /bin/bash
.PHONY:
.SECONDARY:

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
# --------------------------------------------------------------------------- #
# ######################## Cat People Data Processing ####################### #
# --------------------------------------------------------------------------- #
data/catpeople_baseline_nb.dev: $(CATPEOPLE_DIR)/catpeople_clean_segmented_context.shelf data/cat-people-dev.fold.pkl
	./catpeople_baseline_nb.py --in_shelf $< --fold_fn $(word 2,$+)

ifeq ($(shell domainname),clsp)
  CATPEOPLE_DIR := /export/b15/prastog3
else
  CATPEOPLE_DIR := data
endif

$(CATPEOPLE_DIR)/catpeople_clean_segmented_context.shelf: $(CATPEOPLE_DIR)/catpeople_wikilink_mentions.shelf.dat
	./catpeople_clean_segmented_context.py \
	  --in_shelf $(basename $<) \
	  --out_shelf $@ 2> $@.log

# ----------------------------------- #
# The Cat People Mentions in Wikilink #
# ----------------------------------- #
$(CATPEOPLE_DIR)/catpeople_wikilink_mentions.shelf.dat: data/wiki_link /export/b15/prastog3/wikilinks data/cat-people
	./extract_person_mentions_from_wikilink_data.py \
	  --thrift_class_dir $< \
	  --thrift_data_dir $(word 2,$+) \
	  --human_entity_fn $(word 3,$+) \
	  --out_fn $@

# ---------------------- #
# The Cat People Dataset #
# ---------------------- #
# 7814 Categories # 58943 Unique URLs
data/cat-people: data/chosen_url_all_mthresh~10
	cp $<  $@

data/cat-people-dev.fold.pkl: data/cat-people-dev
	./catpeople_dev.fold.py --seed 1234 --in_fn $< --out_fn $@ --fold 3

# 100 Categories # 2519 Unique URLs
data/cat-people-dev: data/chosen_url_100_mthresh~10
	cp $< $@

# --------------------------------------------------------- #
# Wiki link data pilot processing, This was called wiki_Use #
# --------------------------------------------------------- #
data/entity_descriptors_procoref~%.psv:
	./wikimic_pilot.mk $@

# ------------------------------------------------------------------ #
# Use DBPedia and Wikilinks Datasets to create a list of chosen urls #
# ------------------------------------------------------------------ #
data/chosen_url_%_mthresh~10:
	./chosen_url.mk $@

# --------------------------- #
# Process the ACE 2005 corpus #
# --------------------------- #
process_ace:
	./ace_2005.mk data/unique_human_entities

# ------------------------------------------------------------------------- #
# Create thrift classes to read the wikilinks dataset that was released by  #
# Sameer Singh et. al. This dataset was created by mining web links         #
# pointing to Wikipedia pages.                                              #
# ------------------------------------------------------------------------- #
data/wiki_link: data/wiki-link-v0.1.thrift
	thrift -gen py:new_style $< ; mv gen-py $@
