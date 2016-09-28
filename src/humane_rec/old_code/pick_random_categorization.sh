#!/usr/bin/env bash
category=$(\ls data/category_to_entities/ | gshuf | head -1)
ID=$(echo $category | gsha1sum | cut -c -8)
fgrep -f data/category_to_entities/$category data/entity_descriptors_procoref~0.psv > data/random/details/$ID.$category
cut -d '|' -f 4- data/random/details/$ID.$category > data/random/$ID
