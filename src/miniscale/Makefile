SHELL := /bin/bash
ning_dir := /home/hltcoe/ngao/miniScale-2016/Enron
store := /export/projects/prastogi/kbvn
seed := 1234
PATH_MAXLENGTHS := 5 100
DEBUG ?= echo

all:
	echo 'Specify a proper target. Read the Makefile.'  $@

#-----------------------------#
# COMMANDS FOR Kelvin KB Task #
#     Vertex Nomination       #
#-----------------------------#
VERTEX_NAME_FN := /export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.vertexnames
make_all_text:
	for f in /export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_*_logistic_training_acc.pickle ; do  \
	    printf '%-130s' $$(basename $$f); $(DEBUG) $(MAKE) -B -s $${f%pickle}txt; \
	done

/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_%_training_acc.txt: /export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_%_training_acc.pickle
	python -c 'import sys; import cPickle as pkl; from pprint import pprint;  data = pkl.load(open("$<")); ([pprint(k) for k in data.items()]); print >> sys.stderr, "macro_average", sum(data.values()) / len(data)' 1> $@

QSUB := qsub -b y -q all.q -l num_proc=1,mem_free=2G,h_rt=100:00:00 -V -j y -r yes -m a -M prastog3@jhu.edu -cwd ./submit_grid_stub.sh

# Kelvin.BinaryCoMentionGraph.features_maxd~100_ProjectToSphere~FALSE_Laplacian~FALSE_dimkept~100 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~100_ProjectToSphere~FALSE_Laplacian~TRUE_dimkept~100 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~100_ProjectToSphere~FALSE_Laplacian~TRUE_dimkept~78 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~100_ProjectToSphere~TRUE_Laplacian~FALSE_dimkept~100 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~100_ProjectToSphere~TRUE_Laplacian~TRUE_dimkept~100 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~100_ProjectToSphere~TRUE_Laplacian~TRUE_dimkept~78 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~FALSE_Laplacian~FALSE_dimkept~200 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~FALSE_Laplacian~FALSE_dimkept~6 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~TRUE_Laplacian~FALSE_dimkept~200 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~TRUE_Laplacian~FALSE_dimkept~6 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~25_ProjectToSphere~FALSE_Laplacian~FALSE_dimkept~10 
# 	    Kelvin.BinaryCoMentionGraph.features_maxd~25_ProjectToSphere~TRUE_Laplacian~FALSE_dimkept~10 
create_all:
	for f in \
	 Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~FALSE_Laplacian~TRUE_dimkept~165 \
	 Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~FALSE_Laplacian~TRUE_dimkept~200 \
	 Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~TRUE_Laplacian~TRUE_dimkept~165 \
	 Kelvin.BinaryCoMentionGraph.features_maxd~200_ProjectToSphere~TRUE_Laplacian~TRUE_dimkept~200 \
	; do \
	    $(DEBUG) $(QSUB) /export/projects/prastogi/kbvn/$${f}_logistic_probability & \
	done

# /export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_maxd~25_ProjectToSphere~FALSE_Laplacian~FALSE_dimkept~10
/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_maxd~%_logistic_probability: /export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_maxd~%
	./classifier.py --seed 1234 \
	  --vertex_feature_fn $< \
	  --output_fn_prefix $@

# This creates files like:
# "/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_maxd~30_ProjectToSphere~FALSE_Laplacian~FALSE"
# "/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features_maxd~30_ProjectToSphere~TRUE_Laplacian~FALSE"
# make maxd=100 dim_override=50 LAPLACIAN=FALSE /export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features
# make maxd=100 dim_override=100 LAPLACIAN=TRUE /export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features 
maxd ?= 30
dim_override ?= 30
LAPLACIAN ?= FALSE
/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features: /home/hltcoe/ngao/miniScale-2016/Kelvin/BinaryCoMentionGraph
	R -q -e "source('VN1.R'); main(maxd=$(maxd), Laplacian=$(LAPLACIAN), graph_fn='$<', vertex_feature_save_fn='$(word 1,$(subst _, ,$@))', vertex_name_save_fn='$(VERTEX_NAME_FN)', dim_override=$(dim_override))"


#---------------------------#
# COMMANDS FOR THE ENRON KB #
#      Entity Linking ################
# TARGET: rt_contactGraph
#         rt_normalizedContactGraph
rt_%: 
	for agg in mean max ; do \
	  for path_maxlength in $(PATH_MAXLENGTHS); do \
	    for n_runs in 50; do \
	        $(MAKE) $(store)/enron_$*_seed~$(seed)_length~$${path_maxlength}_reps~$${n_runs}_agg~$${agg}.rating; \
	done; done; done

$(store)/enron_%_agg~mean.rating: $(store)/enron_%.pickle
	./aggregate_walk_into_flatfile_rating.py \
	    --pkl_fn $< \
	    --agg mean \
	    --out_fn $@ 

$(store)/enron_%_agg~max.rating: $(store)/enron_%.pickle
	./aggregate_walk_into_flatfile_rating.py \
	    --pkl_fn $< \
	    --agg max \
	    --out_fn $@ 

#----------------------------------------------------#
# Do the random walks. This creates the pickle files 
# containing the statistics from the random walks.
# TARGET: rw_contactGraph
#         rw_normalizedContactGraph
#----------------------------------------------------#
rw_%: 
	for path_maxlength in $(PATH_MAXLENGTHS); do \
	    for n_runs in 50; do \
	        $(MAKE) graphtype=$* path_maxlength=$${path_maxlength} n_runs=$${n_runs} $(store)/enron_$*_seed~$(seed)_length~$${path_maxlength}_reps~$${n_runs}.pickle; \
	done; done

$(store)/enron_%.pickle: 
	./random_walk_on_optimized_datastructure.py \
	    --seed $(seed) \
	    --path_maxlength $(path_maxlength) \
	    --n_runs $(n_runs) \
	    --graph_fn $(store)/optimal4randomwalk_enron_$(graphtype).pickle \
	    --query_fn $(ning_dir)/queries \
	    --out_fn $@ 

# TARGET: optimal4randomwalk_enron_contactGraph.pickle
#         optimal4randomwalk_enron_normalizedContactGraph.pickle
$(store)/optimal4randomwalk_enron_%.pickle: $(ning_dir)/$*
	./create_locally_weighted_adj_list_from_flatfile.py \
	    --fn $(ning_dir)/$* \
	    --out_fn $@

VN1:
	R -q -e "source('VN1.R'); VN1()"
