#!/usr/bin/env bash
# Based on https://github.com/jiepujiang/cs646_tutorials
# UMASS CS646 Information Retrieval (Fall 2016)
# A Simple Tutorial of Galago and Lucene (for CS646 Students)
indexPath=${1-~/export/kbmvlsa/dbpedia.trecweb.galago}
trecweb_file=${2-`./config.sh TREC_WEB_DBPEDIA_GZ`}
test -f $trecweb_file || exit 89
test -d $indexPath || mkdir -p $indexPath
set -x
# Calling galago build will show more flags including methods for running
# distributed jobs.
exec galago build \
       --indexPath=$indexPath \
       --inputPath+$trecweb_file\
       --nonStemmedPostings=true\
       --stemmedPostings=true\
       --stemmer+krovetz \
       --corpus=true\
       --tokenizer/fields+names\
       --tokenizer/fields+category\
       --tokenizer/fields+attributes\
       --tokenizer/fields+SimEn\
       --tokenizer/fields+RelEn\
       --server=true\
       --port=60000\
       --mode=threaded
# /Users/pushpendrerastogi/data/galago-3.10/galago-3.10/core/src/main/java/
# org/lemurproject/galago/core/tools/App.java
# galago build [flags] --indexPath=<index> (--inputPath+<input>)+
