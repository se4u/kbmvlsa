SHELL := $(shell echo $$SHELL)
.SECONDARY:

echo_%:
	echo $($*)

DTM := $(HOME)/export/kbmvlsa/dbpedia.trecweb.make
DTCAT := $(shell ./config.sh TREC_WEB_CATEGORIES_STR)
TREC_WEB_DBPEDIA := $(shell ./config.sh TREC_WEB_DBPEDIA)
# The dictionary that maps tokens to their counts in the xml file. (A vocabulary)
TREC_WEB_TOKEN_PKL := $(shell ./config.sh TREC_WEB_TOKEN_PKL)
# The dictionaries that maps tokens to their index in the array.
TREC_WEB_HIT_LIST_PKL := $(shell ./config.sh TREC_WEB_HIT_LIST_PKL)
# The hit list arrays.
TREC_WEB_HIT_LIST_NPZ := $(shell ./config.sh TREC_WEB_HIT_LIST_NPZ)

# ------------------- #
# Evaluate Embeddings #
# ------------------- #
# Learn a feature vector for all possible combinations.
# Using the SVM^{rank} method.
eval:
	./eval.py

# Convert queries, and query words, into vectors.

# ------------------------------------------------------ #
# Perform MVLSA to create a single embedding from the KB #
# ------------------------------------------------------ #
# Embed/
#  ➕ lib_embed_entity
#    ➕━━ class_composable_transform
#    ➕━━ lib_linalg
#    ➕━━ ~~class_pmi_transformer~~
#  ➕ test_lib_embed_entity
# target := Mvlsa@[mvlsa_opt] | CONCAT
# mvlsa_opt := (final_dim~[num]@)?\
#              (intemediate_dim~[num]@)?\
#              (view_transform~[str]@)?\
#              (row_weighting~[word]@)?\
#              (mean_center~[bool]@)?
# num := \d(\.\d)?
# word := [a-zA-Z0-9]+
# bool := True | False

rsyncx := rsync -avz -vi --progress --partial-dir=/tmp/rsync-partial
rsync_to_coe:
	for f in '~/data/chen-xiong-EntityRankData/dbpedia.trecweb/dbpedia.trecweb.small' \
	   '~/data/chen-xiong-EntityRankData/dbpedia.trecweb.gz'  \
	   '~/export/kbmvlsa/dbpedia.trecweb.*' ;\
	do \
	  echo $(rsyncx) $$f coe:`echo "$${f%/*}"`/ ; \
	done
# ------------------------------------------ #
# Cython based processing of dbpedia.trecweb #
# ------------------------------------------ #
$(TREC_WEB_HIT_LIST_NPZ) $(TREC_WEB_HIT_LIST_PKL) $(TREC_WEB_TOKEN_PKL):
	$(MAKE) -c cython $(TREC_WEB_HIT_LIST_NPZ)

# ------------ #
# Random Stuff #
# ------------ #
QUERIES=~/data/dbpedia-entity-search-test-collection/queries.txt
unique_tokens_%: $(%)
	cut -d'	' -f 2- $($*) | tr ' ' '\n' | sed '/^\s*$$/d' | sort -u

# I converted the original queries to better looking queries by
# 1. Taking care of apstrophes, remove traling aprostrophes
# 2. Splitting hyphens
# 3. Removing other punctuation
# 4.
assert_mvlsa_embeddings_exist_for_query_tokens: ~/data/embedding/mvlsa/combined_embedding_0.words.txt
	export LC_ALL='C'; join -v 1 \
	 <(make -s unique_tokens_QUERIES | awk '{print tolower($0)}' | sort ) \
	 <(awk '{print tolower($0)}' $<  | sort )
