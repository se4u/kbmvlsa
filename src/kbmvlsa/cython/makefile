# CFLAGS := $(shell python-config --cflags)
# LDFLAGS := $(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_config_var('LDSHARED')") -lpython2.7

echo_%:
	echo $($*)

clean:
	-rm *.o
	-find . -name '*.cpp' ! -name 'KrovetzStemmer.cpp' -type f -maxdepth 1 -exec rm {} +
	-rm -r build/
	-rm __init__*
	-python setup.py clean
	-python setup_re2.py clean

small: small_999988 small_99990 small_9988 small_990
small_%:
	head -$* `../config.sh TREC_WEB_DBPEDIA` > `../config.sh TREC_WEB_DBPEDIA_SMALL`


run: xml2cscformat.so
	PYTHONPATH=.. python -c \
	  'from xml2cscformat import *; main(parse_args())' \
	  --infn `../config.sh TREC_WEB_DBPEDIA` \
	  --field_token_index_fn `../config.sh TREC_WEB_TOKEN_PKL` \
	  --outpkl `../config.sh TREC_WEB_HIT_LIST_PKL` \
	  --outnpz `../config.sh TREC_WEB_HIT_LIST_NPZ`

test: xml2cscformat.so
	$(MAKE) small_990
	PYTHONPATH=.. python -c \
	  'from xml2cscformat import *; main(parse_args())' \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL` \
	  --field_token_index_fn /tmp/tmp.pkl \
	  --outpkl /tmp/tmp.hit_list.pkl \
	  --outnpz /tmp/tmp.hit_list.npz
	./test_xml2cscformat.py /tmp/tmp.hit_list.pkl /tmp/tmp.hit_list.npz

xml2cscformat.so: setup_xml2cscformat.py xml2cscformat.pyx Fielded_hit_list.pyx
	python $< build_ext --inplace

tabsep_line: profile_line
tabsep_profile: tabsep_profile_c
tabsep_profile_%:
	python setup_xmltabsep_profiling.py build_ext --inplace
	PYTHONPATH=.. ./profile.py $* \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL`\
	  --outfn /tmp/tmp.pkl

tabsep_run: xml2tabsep.so
	PYTHONPATH=.. python -c \
	  'from xml2tabsep import *; args=parse_args(); dict_list=main(args); save(args, dict_list)' \
	  --infn `../config.sh TREC_WEB_DBPEDIA` \
	  --outfn `../config.sh TREC_WEB_TOKEN_PKL`

tabsep_test: xml2tabsep.so
	$(MAKE) small_990
	PYTHONPATH=.. python -c \
	  'from xml2tabsep import *; args=parse_args(); dict_list=main(args); save(args, dict_list)' \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL` --outfn /tmp/tmp.pkl
	python test_tmp.pkl.py

xml2tabsep.so: xml2tabsep.pyx analyzer.pyx
	python setup.py build_ext --inplace
