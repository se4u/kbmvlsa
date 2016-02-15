#!/usr/bin/env bash
# Script to setup the packages used for comparing different
# knowledge base completion and vertex nomination strategies
# for the task of vertex nomination.
cd src
# Rescal and Scikit Tensor contain an implementation of "Rescal" that is a good
# baseline method for knowledge base completion.
git submodule add https://github.com/mnick/rescal.py.git
cd rescal.py
python setup.py develop
# Junto contains code for label propagation.
git clone https://github.com/parthatalukdar/junto.git
