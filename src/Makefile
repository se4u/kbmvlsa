SHELL := /bin/bash
ning_dir := /home/hltcoe/ngao/miniScale-2016/Enron
store := /export/projects/prastogi/kbvn
seed := 1234

all:
	echo 'Specify a proper target. Read the Makefile.'  $@


# TARGET: rw_contactGraph
#         rw_normalizedContactGraph
rw_%: 
	for path_maxlength in 10 25 50; do \
	    for n_runs in 50; do \
	        $(MAKE) graphtype=$* path_maxlength=$${path_maxlength} n_runs=$${n_runs} $(store)/enron_$*_seed~$(seed)_length~$${path_maxlength}_reps~$${n_runs}.pickle; \
	done; done

# TARGET: rt_contactGraph
#         rt_normalizedContactGraph
rt_%: 
	for agg in mean max ; do \
	for path_maxlength in 10 25 50; do \
	    for n_runs in 50; do \
	        $(MAKE) $(store)/enron_$*_seed~$(seed)_length~$${path_maxlength}_reps~$${n_runs}_agg~$${agg}.rating; \
	done; done; done

$(store)/enron_%_agg~mean.rating: 
	./aggregate_walk_into_flatfile_rating.py \
	    --pkl_fn $(store)/enron_$*.pickle \
	    --agg mean \
	    --out_fn $@ 

$(store)/enron_%_agg~max.rating: 
	./aggregate_walk_into_flatfile_rating.py \
	    --pkl_fn $(store)/enron_$*.pickle \
	    --agg max \
	    --out_fn $@ 

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
