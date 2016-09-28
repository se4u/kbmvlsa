#!/usr/bin/env make -f
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
