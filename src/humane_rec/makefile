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
ifeq ($(shell domainname),clsp)
  CATPEOPLE_DIR := /export/b15/prastog3
else
  CATPEOPLE_DIR := data
endif

# --------- #
# Reporting #
# --------- #
catpeople_perf_metric:
	for ngramocc in 0.2 0.6 0.7 ; do \
	 ./catpeople_baseline_nb.py --evaluate 0 --report_pkl_fn data/performance_aggregator_$${ngramocc}.pkl; done

catpeople_statistics:
	./catpeople_baseline_nb.py --evaluate 0 --data_stats 1 --cat2url_fn data/cat-people

# ---------------------- #
# Cat People Experiments #
# ---------------------- #
data/performance_aggregator_%.pkl: $(CATPEOPLE_DIR)/catpeople_clean_segmented_context.shelf data/cat-people-dev.fold.pkl
	./catpeople_baseline_nb.py --in_shelf $< --fold_fn $(word 2,$+) --report_pkl_fn $@


# -------------------------- #
# Cat People Data Processing #
# -------------------------- #
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
