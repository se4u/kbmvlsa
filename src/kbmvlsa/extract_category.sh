#!/usr/bin/env bash
7z e -so `./config.sh TREC_WEB_DATA_DIR` \
    | awk 'BEGIN{print "<XML>"}{print $0}END{print "</XML>"}' \
    | python util_trecweb_parser.py
