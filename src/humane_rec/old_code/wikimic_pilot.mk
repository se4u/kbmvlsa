#!/usr/bin/make -f wikimic_pilot.mk
SHELL := /bin/bash
.PHONY:
.SECONDARY:
default:
	echo "Specify Target"
echo_%:
	echo $($*)


# ----------------------- WIKILINKS DATA PROCESSING ----------------------- #
# Extract entity mentions from wiki link corpus that contains real mentions #
# of entities in the form of links from web pages to wikipedia articles.    #
# Data is stored as thrift communications. The pkl files contains a map     #
# from entities in the `human_entity_fn` to a list of mentions stored in    #
# the `thrift_data_dir`. The data in `thrift_data_dir` has to be read using #
# the classes in `thrift_class_dir`                                         #
# ------------------------------------------------------------------------- #
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

# There are 371 entities, each with 127642 sentences about them.
# I want to parse these sentences as quickly and as good as possible.
# For the kind of descriptions that I want to draw, extra accuracy may not
# be necessary, but still it will be nice to be able to use PMP parses.
# In 35 minutes, it parsed 44776 sentence,
# In 110 minutes we parsed 156,652 sentences.
# We have 415397 sentences, total time is 5 hours.
parse_on_r6n24: # Do not run docker in tty mode.
	zcat wikimic_extract_sentence_boundary.txt.gz \
	  | docker run -i syntaxnet-parser 2> /dev/null \
	  | gzip -9 > wikimic_tokenize_parse_sentence.conll.gz

copy_to_r6n24: data/wikimic_extract_sentence_boundary.txt.gz
	scp $< prastog3@login.clsp.jhu.edu:/home/prastog3/
	ssh prastog3@login.clsp.jhu.edu "rsync --progress -av -e ' ssh -A -t prastogi@test1.hltcoe.jhu.edu ssh -A -t prastogi@r6n24 ' /home/prastog3/$(notdir $<) :/home/hltcoe/prastogi/ "

data/wikimic_extract_sentence_boundary.txt.gz: data/wikimic_extract_sentence_boundary.pkl
	python -c 'from __future__ import print_function; from cPickle import load; data = load(open("$<")); [print(s) for k in data for m in data[k] for s in m["sentences"]]' | gzip -9 > $@

data/wikimic_extract_sentence_boundary.pkl: data/wikimic_remove_translate_nonascii.pkl
	./wikimic_extract_sentence_boundary.py --in_fn $< --out_fn $@

data/wikimic_remove_translate_nonascii.pkl: data/wiki_link_individual_mentions.pkl
	./wikimic_remove_translate_nonascii.py --in_fn $< --out_fn $@

# USAGE: See wiki_link_individual_mentions.ipynb
# Basically it contains all the facts in the wikilinks data about `371`
data/wiki_link_individual_mentions.pkl: data/wiki_link /export/b15/prastog3/wikilinks
	./extract_person_mentions_from_wikilink_data.py \
	  --thrift_class_dir $< \
	  --thrift_data_dir $(word 2,$+) \
	  --out_fn $@ # --human_entity are  HARDCODED in file.
