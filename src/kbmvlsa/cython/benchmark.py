#+BEGIN_SRC python
import config
import timeit
import re
import re2
# The slow_re_pattern is almost 15 times slower :O
slow_re_pattern = '<%s> *(.+?) *</%s>.+?'
fast_re_pattern = '<%s> *(.+) *</%s>.+?'
re_pattern = ' *<DOC>.*?%s</DOC>'%(''.join(
    fast_re_pattern%(e, e)
    for e
    in ["DOCNO", "DOCHDR", "names", "category", "attributes", "SimEn", "RelEn"]))
data = open(config.TREC_WEB_DBPEDIA_SMALL).read().replace('\n', ' ')
re_pattern = re.compile(re_pattern)
re2_pattern = re2.compile(re_pattern)

def re_f():
    global data
    for m in re_pattern.finditer(data):
        dd = tuple(m.groups())

def re2_f():
    global data
    for m in re2_pattern.finditer(data):
        dd = tuple(m.groups())

number = 10000
print(timeit.timeit("re_f()",
                    setup="from __main__ import re_f, data, re_pattern",
                    number=number))
print(timeit.timeit("re2_f()",
                    setup="from __main__ import re2_f, data, re2_pattern",
                    number=number))
#+END_SRC
