import re
import config
fast_re_pattern = '<%s> *(.+?) *</%s>.+?'
re_pattern = ' *<DOC>.*?%s</DOC>'%(''.join(
    fast_re_pattern%(e, e)
    for e
    in config.TREC_WEB_CATEGORIES))

xml_matcher = re.compile(re_pattern)
docno_matcher = re.compile(" *<DOC>.*?<DOCNO> *(.+?) *</DOCNO>")
