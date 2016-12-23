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


line: profile_line
profile: profile_c
profile_%:
	python setup_xmltabsep_profiling.py build_ext --inplace
	PYTHONPATH=.. ./profile.py $* \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL`\
	  --outfn /tmp/tmp.pkl

run: xml2tabsep.so
	PYTHONPATH=.. python -c \
	  'from xml2tabsep import *; args=parse_args(); dict_list=main(args); save(args, dict_list)' \
	  --infn `../config.sh TREC_WEB_DBPEDIA` \
	  --outfn `../config.sh TREC_WEB_TOKEN_PKL`

test: xml2tabsep.so
	$(MAKE) small_990
	PYTHONPATH=.. python -c \
	  'from xml2tabsep import *; args=parse_args(); dict_list=main(args); save(args, dict_list)' \
	  --infn `../config.sh TREC_WEB_DBPEDIA_SMALL` --outfn /tmp/tmp.pkl
	python test_tmp.pkl.py

xml2tabsep.so: xml2tabsep.pyx analyzer.pyx
	python setup.py build_ext --inplace
