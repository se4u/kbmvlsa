#!/usr/bin/make -f
QSUB := qsub -b y -V -j y -r yes -l mem_free=80G,arch=*64*,h_rt=100:00:00,num_proc=4 -cwd
run:
	for vt in IDENTITY SQROOT TFIDF NORM_TFIDF TF NORM_TF LOG_TFIDF; do \
	  $(QSUB) exec ./makefile run_Mvlsa@intermediate_dim~300@view_transform~$${vt}@mean_center~0; done

run_%:
	source activate multithreaded_numpy && PYTHONPATH=..:../cython exec python lib_embed_entity.py --config $*
