#!/usr/bin/env bash
# Script to setup the packages used for comparing different
# knowledge base completion and vertex nomination strategies
# for the task of vertex nomination.
cd ~/tools
# Rescal and Scikit Tensor contain an implementation of "Rescal" that is a good
# baseline method for knowledge base completion. 
git clone https://github.com/mnick/rescal.py.git
git clone https://github.com/mnick/scikit-tensor.git
# Junto contains code for label propagation.
git clone https://github.com/parthatalukdar/junto.git
