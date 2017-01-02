#!/usr/bin/env python
'''
| Filename    : setup_matrix_multiply_inplace.py
| Description :
| Author      : Pushpendre Rastogi
| Created     :
| Last-Updated:
|           By: Pushpendre Rastogi
|     Update #: 0
'''
from setup import main
main(extension_ns=(("matrix_multiply_inplace", ("matrix_multiply_inplace.pyx",)),))
