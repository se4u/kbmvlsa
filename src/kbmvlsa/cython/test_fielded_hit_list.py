#!/usr/bin/env python
from fielded_hit_list import FieldedHitList
fhl = FieldedHitList(2, [3, 4])
print fhl.field_token_doc_count
print dir(fhl)
fhl.update(0, 1, 234)
fhl.update(0, 1, 234)
fhl.update(0, 1, 235)
print fhl.field_token_doc_count
