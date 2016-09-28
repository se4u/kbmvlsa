grep "$2" data/parsed_mentions  | awk -F'\\|\\|\\|' 'BEGIN{OFS="\t"}{print $9, $11, $8}' | sort -u > $1/${2// /_}
