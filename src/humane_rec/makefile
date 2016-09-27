# ----- #
# Setup #
# ----- #
SHELL := /bin/bash
.PHONY:
.SECONDARY:
default:
	echo "Specify Target"
echo_%:
	echo $($*)
CLSP_DIR := /home/prastog3/projects/kbvn/src/humane_rec
CLSP_CPD := /export/b15/prastog3
ifeq ($(shell domainname),clsp)
  CPD := $(CLSP_CPD)
else
  CPD := data
endif


rsync1:
	rsync -avz *.py prastog3@b15:$(CLSP_DIR)/
	rsync -avz makefile prastog3@b15:$(CLSP_DIR)/
	rsync -avz data/cat-people-dev* prastog3@b15:$(CLSP_DIR)/data/

rsync2:
	rsync -avz prastog3@b15:$(CLSP_CPD)/catpeople_clean_segmented_context.shelf* $(CPD)/


# --------- #
# Reporting #
# --------- #
catpeople_perf_metric:
	for ngramocc in 0.2 0.6 0.7 ; do \
	 ./catpeople_baseline_nb.py --evaluate 0 --report_pkl_fn data/performance_aggregator_$${ngramocc}.pkl; done

catpeople_statistics:
	./catpeople_baseline_nb.py --evaluate 0 --data_stats 1 --cat2url_fn data/cat-people

data/performance_aggregator_%.pkl: $(CPD)/catpeople_clean_segmented_context.shelf data/cat-people-dev.fold.pkl
	echo ./catpeople_baseline_nb.py --report_pkl_fn $@ --df_lim 0.2

show_step3_features:
	./catpeople_baseline_nb.py   --evaluate 0 --show_step3_features 1 --df_lim 0.2

update_shelf: $(CPD)/catpeople_clean_segmented_context.shelf.dat
	./catpeople_baseline_nb.py \
	  --evaluate 0 \
	  --update_shelf 1 \
	  --in_shelf $(basename $<)

# ---------------------- #
# Cat People Experiments #
# ---------------------- #
# CPXP: First arg is ppcfg, second arg in expcfg #
CPXP = $(CPD)/catpeople_experiment.ppcfg~$(1).expcfg~$(2).pkl
xpmln: $(foreach expcfg,300 301 302,$(foreach ppcfg,1 8,$(call CPXP,$(ppcfg),$(expcfg))))
xpnbk: $(foreach expcfg,100 101,$(foreach ppcfg,1 8,$(call CPXP,$(ppcfg),$(expcfg))))
xpnb: $(foreach expcfg,0,$(foreach ppcfg,0 7,$(call CPXP,$(ppcfg),$(expcfg))))

XTRACT = $(subst ~, ,$(subst ., --,$(1)))
$(CPD)/catpeople_experiment%.pkl:
	$(MAKE) $(CPD)/catpeople_pp_$(word 2,$(call XTRACT,$*))
	./catpeople_experiment.py  $(call XTRACT,$*)
# -------------------------- #
# Cat People Data Processing #
# -------------------------- #
allpp:
	for n in 0 1 4 7 8 11; do $(MAKE) $(CPD)/catpeople_pp_$$n; done

unigram: $(CPD)/catpeople_pp_0
univec: $(CPD)/catpeople_pp_1
dsctok: $(CPD)/catpeople_pp_4

$(CPD)/catpeople_pp_%: $(CPD)/catpeople_clean_segmented_context.shelf.dat
	./catpeople_preprocessor.py --in_shelf $(basename $<) --config $*

$(CPD)/catpeople.parse.pkl: $(CPD)/catpeople_clean_segmented_context.shelf.dat $(CPD)/catpeople.parse.gz
	./catpeople_preprocessor_parses_to_pkl.py \
	  --in_shelf $(basename $<) \
	  --parsefn $(word 2,$+) \
	  --parse_pkl $@

$(CPD)/catpeople.parse.gz:
	rsync -v r6n23:~/data/catpeople.parse.gz*  $(CPD)/
	rsync -v r6n25:~/data/catpeople.parse.gz*  $(CPD)/
	zcat $(CPD)/catpeople.parse.gz[0123] | gzip > $@

commands_to_run:
	ssh r6n23 'nohup ~/data/catpeople_parser.sh 0 >&- 2>&- <&- &'
	ssh r6n23 'nohup ~/data/catpeople_parser.sh 1 >&- 2>&- <&- &'
	ssh r6n25 'nohup ~/data/catpeople_parser.sh 2 >&- 2>&- <&- &'
	ssh r6n25 'nohup ~/data/catpeople_parser.sh 3 >&- 2>&- <&- &'

deploy_catpeople.conll:
	rsync -v /export/b15/prastog3/catpeople.conll.gz0 r6n23:~/data/
	rsync -v /export/b15/prastog3/catpeople.conll.gz1 r6n23:~/data/
	rsync -v catpeople_parser.sh r6n23:~/data/
	rsync -v /export/b15/prastog3/catpeople.conll.gz2 r6n25:~/data/
	rsync -v /export/b15/prastog3/catpeople.conll.gz3 r6n25:~/data/
	rsync -v catpeople_parser.sh r6n25:~/data/

$(CPD)/catpeople.conll.gz: $(CPD)/catpeople_clean_segmented_context.shelf.dat
	./catpeople_preprocessor.py --print_to_conll 1 --in_shelf $(basename $<)  --out_fn $@

$(CPD)/catpeople_clean_segmented_context.shelf: $(CPD)/catpeople_wikilink_mentions.shelf.dat
	./catpeople_clean_segmented_context.py \
	  --in_shelf $(basename $<) \
	  --out_shelf $@ 2> $@.log

# ----------------------------------- #
# The Cat People Mentions in Wikilink #
# ----------------------------------- #
$(CPD)/catpeople_wikilink_mentions.shelf.dat: data/wiki_link /export/b15/prastog3/wikilinks data/cat-people
	./extract_person_mentions_from_wikilink_data.py \
	  --thrift_class_dir $< \
	  --thrift_data_dir $(word 2,$+) \
	  --human_entity_fn $(word 3,$+) \
	  --out_fn $@

# -------------------------------------- #
# The CatPeople Category -> URL Map file #
# 7814 Categories; 58943 Unique URLs     #
# -------------------------------------- #
data/cat-people: data/chosen_url_all_mthresh~10
	cp $<  $@

data/cat-people-dev.fold.pkl: data/cat-people-dev
	./catpeople_dev.fold.py --seed 1234 --in_fn $< --out_fn $@ --fold 3

# 100 Categories; 2519 Unique URLs
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
