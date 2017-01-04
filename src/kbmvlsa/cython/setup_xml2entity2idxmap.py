#!/usr/bin/env python
from setup import main
name = "xml2entity2idxmap"
main(extension_ns=((name, (name +'.pyx',)),))
