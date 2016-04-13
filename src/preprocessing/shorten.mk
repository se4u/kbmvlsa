#!/usr/bin/make -f
DIR := $(HOME)/data/tackbp2015bbn2
.SECONDARY:


#   44M  confidence_only
#   61M  appearsInDocument    
#   20M  leaf_type
#  132M  sort_base

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
