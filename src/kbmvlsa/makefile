SHELL := $(shell echo $$SHELL)
.PHONY:
.SECONDARY:

echo_%:
	echo $($*)

default:
	echo "Say specific target"

# ---------------------------------------------------------------------- #
# TREC_WEB_DBPEDIA_PFX contains 5 arrays that each contain co-occurrence #
# data that was originally stored in the zipped xml by chen-xiong et al. #
# We just converted it to a matrix                                       #
# ---------------------------------------------------------------------- #
# TREC_WEB_DBPEDIA_PFX := $(shell ./config.sh TREC_WEB_DBPEDIA_PFX)
# $(TREC_WEB_DBPEDIA_PFX):
# 	./util_trecweb_parser.py

setup_galago_on_clsp:
	ssh prastog3@clsp "mkdir -p ~/projects/kbvn/src/kbmvlsa ~/data/chen-xiong-EntityRankData ~/export/kbmvlsa /export/a13/prastog3/dbpedia.trecweb.galago /export/b19/prastog3/dbpedia.trec.python"
	ssh prastog3@clsp "ln -s /export/a13/prastog3/dbpedia.trecweb.galago ~/export/kbmvlsa/"
	ssh prastog3@clsp "ln -s /export/b19/prastog3/dbpedia.trec.python ~/export/kbmvlsa/ "
	rsync -avz ~/data/rasengan prastog3@clsp:~/data
	rsync -avz ~/data/galago-3.10 prastog3@clsp:~/data/
	rsync -avz ./* prastog3@clsp:~/projects/kbvn/src/kbmvlsa/
	rsync --partial-dir=/tmp/rsync-partial --progress -v \
	  ~/data/chen-xiong-EntityRankData/dbpedia.trecweb.gz \
	  prastog3@clsp:~/data/chen-xiong-EntityRankData/

# -b makes rsync backup files that exist in both folders, appending ~ to the old file. You can control this suffix with --suffix .suf
# -u makes rsync transfer skip files which are newer in dest than in src
# -z turns on compression, which is useful when transferring easily-compressible files over slow links
# -vi are for verbosity.
sync_back_from_clsp:
	rsync -abuz -vi --partial-dir=/tmp/rsync_tmp_123 \
	  prastog3@clsp:~/projects/kbvn/src/kbmvlsa/*  kbmvlsa/

# 2. Perform MVLSA on them to create a single embedding.
#    Let the embedding dim be 50.

# 3. Convert the queries into vectors
#    Convert the query words into vectors.

# 4. Learn a feature vector for all possible combinations.
#    Using the SVM^{rank} method.

# 5. Use a learning to rank method on conjunction features.
#    Compute metrics.
eval:
	./eval.py


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
