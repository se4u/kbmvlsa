#!/usr/bin/make -f
# USAGE: ./shorten.mk
# This .mk script extracts features from the tackbp bbn2 database specified in
# $(DIR) using the feature \ edge schema specified in `relationalize_base_graph.yaml`
SHELL := /bin/bash
DIR := $(HOME)/data/tackbp2015bbn2
.SECONDARY:

$(DIR)/relational_bbn2.pkl: $(DIR)/bbn2_cache.pkl $(DIR)/leaf_type relationalize_base_graph.py
	./relationalize_base_graph.py \
	  --out_fn $@ \
	  --cache_fn $< \
	  --leaf_fn $(word 2,$+)

#  .53M  orgToHeadquerter
#   44M  confidence_only
#   61M  appearsInDocument
#   20M  leaf_type
#  132M  sort_base

# Test orgToHeadquerter
test:
	echo 'Test that each grep returns one line'; \
	grep 'f5355f8a-b26c-44e2-b824-76bf5b8102af 738e0227-0c60-4165-a2a7-f8430e0d5b55' $(DIR)/orgToHeadquarter; \
	grep '0d963ed5-c1a6-4cb9-8e5e-142b3c534227 67a32b19-f408-43c0-aee4-5351acfee273' $(DIR)/orgToHeadquarter


FILES:= orgToHeadquarter confidence_only appearsInDocument leaf_type sort_base
BBN_CACHE_DEP := $(foreach var,$(FILES),$(DIR)/$(var) )
$(DIR)/bbn2_cache.pkl: $(BBN_CACHE_DEP)
	./bbn2_cache.py $@ $+

$(DIR)/orgToHeadquarter: $(DIR)/leaf_type $(DIR)/sort_base
	join -2 1 <( grep 'adept-core#OrgHeadquarter' $< | awk '{print $$1}' | sort ) $(word 2,$+) \
	  | fgrep -e location -e organization \
	  | sort -k1,2 -r \
	  | awk '{printf "%s ", $$3; if(NR % 2 == 0){printf "\n";}}' \
	  | sort -k 1 > $@

$(DIR)/confidence_only: $(DIR)/confidence
	grep 'adept-base#confidence' $< | awk '{print $$1, $$3}' | sort -k 1 > $@

$(DIR)/leaf_type: $(DIR)/ont-types
	awk '{print $$1, $$3}' $< | sort -k 1 | ./type_lattice_max_select.py > $@

$(DIR)/appearsInDocument: $(DIR)/metadata
	awk '{print $$1, $$3}' $< | sort -k 1 > $@

$(DIR)/sort_base: $(DIR)/base
	sort -k 1 $< > $@

# Note: this takes 15 minutes on my machine.
# No need to process `other`
shorten_all:
	for f in ont-types base  metadata  ; do \
	$(MAKE) -f shorten.mk DEP=$$f $(DIR)/$$f; done & \
	./shorten.mk DEP=confidence $(DIR)/confidence


# TARGET: make -f shorten.mk -n DEP=base /Users/pushpendrerastogi/data/tackbp2015bbn2/base
$(DIR)/base $(DIR)/confidence $(DIR)/metadata $(DIR)/ont-types $(DIR)/other: $(DIR)/bbn_2016-02-23_13-09-09-$(DEP).nq
	tic=`gdate +%s` ; \
	sed -e 's@<http://adept-kb.bbn.com/adept-data#@@g' \
	  -e 's#<http://www.w3.org/1999/02/##g' \
	  -e 's#<http://adept-kb.bbn.com/##g' \
	  -e 's#<http://www.w3.org/2000/01/##g' \
	  -e 's@\^\^<http://www.w3.org/2001/XMLSchema#float>@@g' \
	  -e 's@\^\^<http://www.w3.org/2001/XMLSchema#date@@g' \
	  -e 's# .$$##g' \
	  -e 's@>@@' \
	  -e 's@>@@' \
	  -e 's@>$$@@' \
	$< > $@ ; \
	toc=`gdate +%s` ; \
	echo Time taken = `expr $$toc - $$tic` seconds
