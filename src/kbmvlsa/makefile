SHELL := $$SHELL
.PHONY:
.SECONDARY:

default:
	echo "Say specific target"

# 1. The goal of my system is to create 5 arrays that contain the fields.
#    Let the embedding dim be 50.


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
