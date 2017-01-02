# The text file that contains the XML data
TREC_WEB_DBPEDIA := $(shell ../config.sh TREC_WEB_DBPEDIA)
# The dictionary that maps tokens to their counts in the xml file. (A vocabulary)
TREC_WEB_TOKEN_PKL := $(shell ../config.sh TREC_WEB_TOKEN_PKL)
# The dictionaries that maps tokens to their index in the array.
TREC_WEB_HIT_LIST_PKL := $(shell ../config.sh TREC_WEB_HIT_LIST_PKL)
# The hit list arrays.
TREC_WEB_HIT_LIST_NPZ := $(shell ../config.sh TREC_WEB_HIT_LIST_NPZ)

# ------- #
# DEFAULT #
# ------- #
echo_%:
	echo $($*)

# ---------------------------- #
# RUN - XML2TABSEP and XML2CSC #
# ---------------------------- #
$(TREC_WEB_HIT_LIST_PKL) $(TREC_WEB_HIT_LIST_NPZ): xml2cscformat.so $(TREC_WEB_TOKEN_PKL)
	PYTHONPATH=.. python -c \
	  'from xml2cscformat import *; main(parse_args())' \
	  --infn `../config.sh TREC_WEB_DBPEDIA` \
	  --field_token_index_fn $(TREC_WEB_TOKEN_PKL) \
	  --outpkl $(TREC_WEB_HIT_LIST_PKL) \
	  --outnpz $(TREC_WEB_HIT_LIST_NPZ)

$(TREC_WEB_TOKEN_PKL): $(TREC_WEB_DBPEDIA) xml2tabsep.so
	PYTHONPATH=.. python -c \
	  'from xml2tabsep import *; args=parse_args(); dict_list=main(args); save(args, dict_list)' \
	  --infn  $< \
	  --outfn $@

# -------------- #
# BUILD AND TEST #
# -------------- #
small: small_999988 small_99990 small_9988 small_990
small_%:
	head -$* `../config.sh TREC_WEB_DBPEDIA` > `../config.sh TREC_WEB_DBPEDIA_SMALL`

SETUP_CMD = python $< build_ext --inplace

matrix_multiply_inplace_test: matrix_multiply_inplace.so
	python test_matrix_multiply_inplace.py

matrix_multiply_inplace.so: setup_matrix_multiply_inplace.py matrix_multiply_inplace.pyx
	$(SETUP_CMD)

xml2cscformat_test: xml2cscformat.so
	$(MAKE) small_990
	PYTHONPATH=.. python -c \
	  'from xml2cscformat import *; main(parse_args())' \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL` \
	  --field_token_index_fn /tmp/tmp.pkl \
	  --outpkl /tmp/tmp.hit_list.pkl \
	  --outnpz /tmp/tmp.hit_list.npz
	./test_xml2cscformat.py /tmp/tmp.hit_list.pkl /tmp/tmp.hit_list.npz

xml2cscformat.so: setup_xml2cscformat.py xml2cscformat.pyx Fielded_hit_list.pyx
	$(SETUP_CMD)

tabsep_test: xml2tabsep.so
	$(MAKE) small_990
	PYTHONPATH=.. python -c \
	  'from xml2tabsep import *; args=parse_args(); dict_list=main(args); save(args, dict_list)' \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL` --outfn /tmp/tmp.pkl
	python test_tmp.pkl.py

xml2tabsep.so: setup.py xml2tabsep.pyx analyzer.pyx
	$(SETUP_CMD)


# ------- #
# PROFILE #
# ------- #
tabsep_line: profile_line
tabsep_profile: tabsep_profile_c
tabsep_profile_%:
	python setup_xmltabsep_profiling.py build_ext --inplace
	PYTHONPATH=.. ./profile.py $* \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL`\
	  --outfn /tmp/tmp.pkl

# ----- #
# CLEAN #
# ----- #
clean:
	-rm *.o
	-find . -name '*.cpp' ! -name 'KrovetzStemmer.cpp' -type f -maxdepth 1 -exec rm {} +
	-rm -r build/
	-rm __init__*
	-python setup.py clean
	-python setup_re2.py clean
