#!/usr/bin/env python
'''
| Filename    : setup_xml2cscformat.py
| Description :
| Author      : Pushpendre Rastogi
| Created     : Sat Dec 24 04:45:42 2016 (-0500)
| Last-Updated: Sat Dec 24 04:54:44 2016 (-0500)
|           By: Pushpendre Rastogi
|     Update #: 1
'''
from setup import main
main(extension_ns=(("xml2cscformat", ("xml2cscformat.pyx",)),
                   ("fielded_hit_list", ("fielded_hit_list.pyx",))))
