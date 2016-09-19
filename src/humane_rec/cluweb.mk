#!/usr/bin/env make -f
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
