#!/usr/bin/env bash
# Script to setup the packages used for comparing different knowledge base
# completion and vertex nomination strategies for the task of vertex nomination.
# ---------------#
#  Download Code #
# ---------------#
cd src/lib
# Rescal and Scikit Tensor contain an implementation of "Rescal" that is a good
# baseline method for knowledge base completion.
git submodule add https://github.com/mnick/rescal.py.git
cd rescal.py
python setup.py develop

# Talukdar's Junto codebase for label propagation.
git submodule add https://github.com/parthatalukdar/junto.git

# Antoine Bordes' KBC Toolkit.
git submodule add https://github.com/glorotxa/SME.git

# Add Rasengan as Submodule
git submodule add https://github.com/se4u/rasengan.git

# ---------------#
#  Download Data #
# ---------------#
cd no_repo/data
# The Presidents Dataset From Nickel et al. ICML 2011
wget http://www.cip.ifi.lmu.de/~nickel/data/us-presidents.rdf.bz2

# Download Dataset for Inferring Missing Entity Type Instances for Knowledge
# Base Completion, by Neelkantan and Ming-Wei Chang
# From http://research.microsoft.com/en-US/downloads/df481862-65cc-4b05-886c-acc181ad07bb/default.aspx
# This download is a large 1GB File.
wget http://ftp.research.microsoft.com/downloads/df481862-65cc-4b05-886c-acc181ad07bb/release_v1.0.zip

# Download Antoine Bordes' TransE Dataset and Code
# Translating Embeddings for Modeling Multi-relational Data
# from https://everest.hds.utc.fr/doku.php?id=en:transe
cd no_repo/data
curl -o fb15k.tgz https://everest.hds.utc.fr/lib/exe/fetch.php?media=en:fb15k.tgz
curl -o semantic_matching_wordnet.tar.gz https://everest.hds.utc.fr/lib/exe/fetch.php?media=en:wordnet-mlj12.tar.gz
curl -o umls_nations_kinships_datasets.tar.gz https://everest.hds.utc.fr/lib/exe/fetch.php?media=en:tensor_factorisation_datasets.tar.gz

# Reidel, Sameer, Tim (Universal Schema)
https://github.com/riedelcastro/riedelcastro.github.com/tree/master/uschema
http://www.riedelcastro.org/uschema/
