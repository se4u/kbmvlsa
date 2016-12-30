## The important files are

1. ~/data/dbpedia-entity-search-test-collection/queries.txt
   query-id <tab> query text
   There are 485 queries.

2. ~/data/dbpedia-entity-search-test-collection/qrels.txt
   query-id <tab> 0 <tab> entity-name <tab> 1
   The qrels file just tells us the dbpedia id of the relevant entities.
   There are 485 queries and a query may have varying number of answers.
   For example, there is 1 query with 1151 answers, and 8 queries with 37 answers
   each, and there are 10 queries with 19 answers. The maximum number of answers a
   query may have is 1151, and the minimum number of answers a query may have is 1.
   The median number of anwers to a query is 9, but the average number of answers
   is just 5

3. ~/data/chen-xiong-EntityRankData/dbpedia.nt.zip
   This file contains the edges between entities in dbpedia.
   There are 3.64M entities of which 1.83M are classified in a 6 level deep
   ontology of 320 classes.

4. ~/data/chen-xiong-EntityRankData/dbpedia.trecweb.zip
   This file contains entity descriptions in TrecWeb format.
   A trectext file contains one or more documents, separated by <DOC> tags.
   <DOCNO>      specifies the document id.
   <DOCHDR>     contains the HTTP request information.
   <names>      Entity names, conventional names of entities.
   <category>   Classes that an entity belongs to.
   <attributes> Entity properties.
   <SimEn>      Aliases.
   <RelEN>      Names of related entities.

5. After processing all this data we end up with
   ~/export/kbmvlsa/dbpedia.trecweb.hit_list.npz
   ~/export/kbmvlsa/dbpedia.trecweb.hit_list.pkl
   ~/export/kbmvlsa/dbpedia.trecweb.field_tokens.pkl
   These files contain the counts of all the data matrices
   and associated metadata.

6. The entire dataset can now be converted into different types of
   co-occurrence based features, using the class of composable transforms.



   All these files can be used extract features of entities, which can then
   be used for learning models of relevance. The simplest way forward will be
   to compute a model for (query, mvlsa) features, and to optimize it using a
   LeToR framework.


6.
For the query feature, I can use word2vec features, or MVLSA features again.

And the shim just needs to be learnt using LeTor.

## The exact experiment will be

1. Compute the embeddings of the entities using MVLSA

2. Use the averaged MVLSA embeddings from the queries

3. Given a dataset of query embeddings, entity embeddings,
   and a set of entities that should be ranked higher than
   other entities, learn a compatibility matrix using learning
   to rank.

4. Compute the MAP@100, P@10, P@20 metrics of the sorted lists.

## Today's Goal

* Run MVLSA on KB
** [X] Create Count Matrices from trecweb format.
*** [X] Perform Tokenization, Lemmatization, Thresholding, Stopword Removal.
    This step took a long time,
    From December 5, through Decmber 12, (one week on EACL in between)
    I tried Lucene, Galago, Cython, CPython, C, C++, basically everything
    I had to learn to process this data.
    The final result was a single file containing the trec web data.
** Evaluate MVLSA
*** Create MVLSA features.
*** Incorporate a wrapped version of learning to rank to run the experiments.
** Prepare count matrices
*** Prepare PMI transformer
**** Write class_pmi_transformer
***** Write PMI
***** Write Dicounted PMI
***** Write Laplace Smoothed PMI
** Prepare an MVLSA runner
*** Write class `Mvlsa` in `lib_embed_entity.py`
**** Check that my existing method for performing MVLSA is not broken.
**** Write method for incremental pca in `lib_linalg`.
**** Add method for better regularized GCCA.
