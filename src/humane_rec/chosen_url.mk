#!/usr/bin/make -f chosen_url.mk
SHELL := /bin/bash
.PHONY:
.SECONDARY:
default:
	echo "Specify Target"
echo_%:
	echo $($*)

CLSP_DIR := /home/prastog3/projects/kbvn/src/humane_rec

data/chosen_url_%_mthresh~10: data/wikilink_category_to_url_and_count_reverse_index.pkl data/chosen_wikilink_categories_%_mthresh~10
	./chosen_url.py --caturl_pkl $< --chosen_cat $(word 2,$+) --mention_thresh 10 > $@
	echo $@ ; cut -d' ' -f 2 $@  | sort -u | wc -l

# -------------------------------------------------------------------- #
# Based on the counts of the wikilink categories, pick a few good ones #
# The basic principle is that I want to chose middle of the road       #
# categories that are neither dominated by a single entity. nor are    #
# too voluminous, neither are they too small                           #
# -------------------------------------------------------------------- #
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
	./wiki_link_url_counts.py
	  --thrift_class_dir $< \
	  --thrift_data_dir $(word 2,$+) \
	  --out_fn $@
