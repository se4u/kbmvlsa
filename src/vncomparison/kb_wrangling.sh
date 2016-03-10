#!/usr/bin/env bash

# ---------------------- #
# Test for superProperty #
# ---------------------- #
# $IFS=$'\n'; for f in $(grep 'subOrganization' bbn_2016-02-23_13-09-09-base.nq | head -20 ); do grep "$( echo $f | sed 's#subOrgan

# ------------------------- #
# Extract Views From the KB #
# ------------------------- #
# while read a b c ; do histog $a $b $c ; done < ~/projects/kbvn/src/vncomparison/adept_kb_binary_relation.dat

# ---------------- #
# Download Dataset #
# ---------------- #
# wget ftp://bbn-99503:LEZ9IP4q@ftp.bbn.com
# for url in $(grep href index.html | cut -c 43- | sed -s 's#".*##g');
# do
#     wget $url ;
# done

# ----------------- #
# Test All Datasets #
# ----------------- #
# while read a b c ; do  tepcs histog_dir/${a}_events_${b} ; tepcs histog_dir/${a}_events_${c} ; done < /home/hltcoe/prastogi/projects/kbvn/src/vncomparison/adept_kb_binary_relation.dat

# Get google url
gog () {
    argum="$1";
    curl -s --get --data-urlencode "q=$1" http://ajax.googleapis.com/ajax/services/search/web?v=1.0 | sed 's/"unescapedUrl":"\([^"]*\).*/\1/;s/.*GwebSearch",//' ;
    echo;
} ;

# Get all named entities in a document.
docx () {
    for e in $( grep $1 bbn_2016-02-23_13-09-09-metadata.nt | awk '{print $1}' | sort -u | cut -c 37-  | rev | cut -c 2- | rev  );
    do
        gca $e ;
    done;
}

# Get random document.
randoc () {
    docid=$( shuf -n 1 document_ids  );
    echo $docid ;
    docx $docid | awk -F'"' '{print $2}'  ;
}

# Get all tuples
gbbn () {
    grep $1 bbn_2016-02-23_13-09-09-* | sed 's#http://adept-kb.bbn.com##g' | sed 's#http://www.w3.org/1999/02/22-rdf-syntax-ns##g' ;
}

# Get canonical string
gca () {
    grep $1 bbn_2016-02-23_13-09-09-base.nq | grep canonicalString ;
}

gont () {
    gbbn $1 | grep ont-type ;
}


## There are zero elements with this relations.
## histog OrganizationPoliticalReligiousAffiliation organization affiliatedEntity ;
## PROBLEM # histog LocatedNear PhyiscalLocation
histog () {
    RELATION=${1-EmploymentMembership};
    ARG1=${2-organization}; # This argument is histogrammed !!
    ARG2=${3-employeeMember};
    # Gather the events, ${ARG1} and ${ARG2}
    set -x;
    cd histog_dir;
    grep "adept-core#${RELATION}" ../bbn_2016-02-23_13-09-09-ont-types.nq | awk '{print $1}' > ${RELATION}_events;
    grep -F -f "${RELATION}_events" ../bbn_2016-02-23_13-09-09-base.nq | grep "core#${ARG1}" | sort  > ${RELATION}_events_${ARG1};
    grep -F -f "${RELATION}_events" ../bbn_2016-02-23_13-09-09-base.nq | grep "core#${ARG2}" |  sort > ${RELATION}_events_${ARG2};
    wc -l "${RELATION}_events" "${RELATION}_events_${ARG1}" "${RELATION}_events_${ARG2}";
    # Count the number of unique ${ARG1}s, how many members they have, and create a histogram.
    awk '{print $3}' "${RELATION}_events_${ARG1}" | sort | uniq -c > "${RELATION}_events_${ARG1}_count";
    awk '{print $1}' "${RELATION}_events_${ARG1}_count" | sort -n -r | uniq -c > "${RELATION}_events_${ARG1}_count_histogram";
    cd ..;
    set +x;
    echo "${RELATION}_events_${ARG1}_count_histogram created";
} ;


# Test that all business events are actually one of bankruptcy / end / merge / start organization
testleaf () {
    NONTERMINAL=${1-BusinessEvent};
    echo Number of NONTERMINAL Events
    grep "core#${NONTERMINAL}" bbn_2016-02-23_13-09-09-ont-types.nq | awk '{print $1}' | wc -l;
    for e in $( grep "core#${NONTERMINAL}" bbn_2016-02-23_13-09-09-ont-types.nq | awk '{print $1}' ); do grep $e bbn_2016-02-23_13-09-09-ont-types.nq | grep -v "core#${NONTERMINAL}" | grep -v "base#" | wc -l  ; done;
}

tepcs () {
    ENTITY_FILE=${1-histog_dir/BeBorn_events_person};
    res=$( join -v 1 <( awk '{print substr($3, 37, 36)}' $ENTITY_FILE | sort ) entities_with_canonical_strings  | wc -l )
    printf '%-70s %d\n' $ENTITY_FILE $res
}
