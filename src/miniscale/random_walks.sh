#!/bin/bash

ning_dir=/home/hltcoe/ngao/miniScale-2016/Enron
store=/export/projects/prastogi/kbvn
seed=1234
for path_maxlength in 5 100
do
    for n_runs in 50
    do
        ./random_walk_on_optimized_datastructure.py \
            --seed $seed \
            --path_maxlength $path_maxlength \
            --n_runs $n_runs \
            --graph_fn $store/optimal4randomwalk_enron_contactGraph.pickle \
            --query_fn $ning_dir/queries \
            --out_fn $store/enron_contactGraph_seed=${seed}_length=${path_maxlength}_reps=${n_runs}.pickle;
    done
done

# for path_maxlength in 10 25 50
# do
#     for n_runs in 50
#     do
#         ./random_walk_on_optimized_datastructure.py \
#             --seed 1234 \
#             --path_maxlength $path_maxlength \
#             --n_runs $n_runs \
#             --graph_fn $store/optimal4randomwalk_enron_normalizedcontactgraph.pickle \
#             --query_fn $ning_dir/queries \
#             --out_fn_prefix enron_normalizedcontact ;
#     done
# done
