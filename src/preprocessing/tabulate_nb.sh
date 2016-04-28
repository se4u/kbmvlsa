#!/usr/bin/env bash
for metric in aupr p10
do
    for e in ''  '.both'  '.max' '.min' '.max.both' '.min.both'
    do
        printf '%-10s %-10s ' $e $metric
        ./tabulate_nb_full_featurization_relational_bbn2.py "$e" $metric
    done
done
