#!/usr/bin/env bash
force_download=${1-0}
MIRRORS=(fr.arxiv.org de.arxiv.org in.arxiv.org es.arxiv.org lanl.arxiv.org arxiv.org)
while read url
do
    output_fn=${url##http*/}
    if ! [[ -e "$output_fn" && $force_download == 0 ]]
    then
        if [[ $url == *"arxiv"* ]]
        then
            rand_idx=$( expr $RANDOM % 6)
            mirror=${MIRRORS[$rand_idx]}
            curl -o "$output_fn" "${url/arxiv.org/$mirror}" 2> /dev/null
        else
            curl -o "$output_fn" "$url" 2> /dev/null
        fi
    fi
    pdfinfo "$output_fn" &> /dev/null
    if ! [ $? -eq 0 ]
    then
        echo Fail $url
    fi
done < <( awk -F, '{if(NR > 44){print substr($5, 2, length($5) - 2)}}' history.csv )
          
          
          
          
