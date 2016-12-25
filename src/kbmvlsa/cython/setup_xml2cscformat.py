#!/usr/bin/env python
'''
| Filename    : setup_xml2cscformat.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Sat Dec 24 04:45:42 2016 (-0500)
| Last-Updated: Sat Dec 24 18:55:07 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 2
'''
from setup import main
main(extension_ns=(("xml2cscformat", ("xml2cscformat.pyx",)),
                   ("analyzer", ("analyzer.pyx", "KrovetzStemmer.cpp")),
                   ("fielded_hit_list", ("fielded_hit_list.pyx",))))
