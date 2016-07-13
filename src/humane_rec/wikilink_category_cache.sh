#!/usr/bin/env bash
in_dir=$1
out_dir=$2
mkdir $out_dir
a=1
while read f
do
    out_file=${f#'api.php?action=query&titles='}
    out_file=${out_file%'&redirects'}
    out_file=${out_file%'&format=json&prop=categories&clshow=!hidden&cllimit=max'}
    jq '.query.pages[].categories[].title' $in_dir/$f > $out_dir/$out_file 2> /dev/null
    output=$?
    if [[ $output == 0 ]]
    then
        : # pass
    elif [[ $output == 5 ]]
    then
        echo $f >> may_need_redirect
    else
        echo $output $in_dir/$f  $out_dir/$out_file
        a=$( expr $a + 1 )
    fi
done < <( \ls -b $in_dir )
echo $a
