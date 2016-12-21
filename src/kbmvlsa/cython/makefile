# CFLAGS := $(shell python-config --cflags)
# # http://stackoverflow.com/questions/25421479
# # clang-and-undefined-symbols-when-building-a-library
# LDFLAGS := $(shell python -c "import distutils.sysconfig; print distutils.sysconfig.get_config_var('LDSHARED')") -lpython2.7

echo_%:
	echo $($*)

clean:
	-rm *.so *.o
	-find . -name '*.cpp' ! -name 'KrovetzStemmer.cpp' -type f -maxdepth 1 -exec rm {} +
	-rm -r build/
	-rm __init__*

deploy:
	cp analyzer.so ../python/

test: analyzer
	python -c 'import $<; assert $<.analyze(u"ABC")==[u"abc"]'

%.so: %.pyx makefile
	python setup.py build_ext --inplace --force
