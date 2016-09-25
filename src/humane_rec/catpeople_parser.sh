#!/usr/bin/env bash
zcat ~/data/catpeople.conll.gz$1 \
    | docker run -i syntaxnet /bin/bash -c "`~/build/demo.sh`" 2> /dev/null \
    | gzip > ~/data/catpeople.parse.gz$1
