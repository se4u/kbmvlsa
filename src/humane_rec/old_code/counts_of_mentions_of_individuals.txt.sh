grep '||| PER ||| Individual ||| NAM |||' $1 \
    | grep -v -P '(NO PAGE|MISSING SENSE|NO_ANNOTATION)' \
    | awk -F' \\|\\|\\| ' '{print $9}' \
    | sort | uniq -c | sort -k 1 -r -n
