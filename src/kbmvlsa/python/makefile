#!/usr/bin/make -f
QSUB := qsub -b y -V -j y -r yes -l mem_free=60G,arch=*64*,h_rt=100:00:00,num_proc=4 -cwd
run:
	for vt in IDENTITY SQROOT TFIDF NORM_TFIDF TF NORM_TF LOG_TFIDF; do \
	  $(QSUB) ./makefile run_Mvlsa@view_transform~SQROOT@mean_center~0; done

run_%:
	PYTHONPATH=..:../cython python lib_embed_entity.py --config $*
