#!/usr/bin/env Rscript
### This script takes an i-graph object a set of starts, walk length and nMC as input
### It runs:
### 1.  nMC independent random walks starting at each of the start vertices
### 2.  Aggregates across all the runs, and computes the number of times each
###     state is visited across all runs
### 3.  Gives as its output a list of all vertices ranked according to how often
###     they were visited across all the runs, along with the associated ranks
###     (so that ties can be seen)
### USAGE: R -q -e "source('random_walk_on_igraph.r'); main()"
library("igraph", verbose=FALSE, warn.conflicts=FALSE)
library("Matrix", verbose=FALSE, warn.conflicts=FALSE)
my.time <- function(){
    ## Return: The Total Time taken.
    proc.time()[3]
}

RW_weighted <- function(g, start, A.matrix, graph.strength.vector,
                        connected.node.list, edge.weights.list,
                        path.maxlength=c(10, 25, 50),
                        n.runs=50){
    ## g is igraph object with weighted edges
    ## start is a vector of start nodes.
    ## if edges unweighted, use built in RW function

    ##-----------------------------------------------------------------#
    ## IMPORTANT NOTE: We assume that the sparse matrix is symmetric.  #
    ## We dont assert that because that would be too inefficient.      #
    ## R `sparseMatrix` class really prefers Column-compressed format  #
    ## Therefore we index by the A.matrix[,state] since that is faster #
    ## Also we really want to get a sparse representation instead of   #
    ## the default dense one therefore we do the hack of getting the   #
    ## indices (Note:A.matrix[,state] is faster than A.matrix[state,]  #
    ## because its in CSmatrix format. we could change it RSparse form #
    ## The sample function afterward is straightforward                #
    ##-----------------------------------------------------------------#

    stopifnot(length(start) == 1) # Right now we only want there to be 1 start.
    visit=rep(NaN, length(V(g)))
    for(i in 1:length(start)){
        for(run in 1:n.runs){
            state=start[i]
            steps=0
            for(steps in 1:path.maxlength){
                connected.node.idx = connected.node.list[[state]]
                edge.weights = edge.weights.list[[state]]

                ## Move forward
                ## Update state and visits.
                state <- sample(
                    connected.node.idx, # Vector of adjacent nodes
                    1, # Number of Samples
                    replace=FALSE,
                    prob=edge.weights / graph.strength.vector[state])
                visit[state] <- visit[state]+1
            }
        }
    }
    return(visit)
}

### There are a 1000 things.
### Each thing takes 90 seconds to run a chain of length 10.
### And it takes 450 sec to run a chain of length 50.
### So it would take 25 hours to run all chains of length 10
### And it would take 125 hours to run all chains of length 50.
### So unless I do a speedup of 125 on single machine, I would have to parallelize.
main <- function(path.maxlength = 10, # 50
                 n.runs=10, #50
                 graph.fn="/export/projects/prastogi/kbvn/enron_contactgraph.graphml",
                 query.fn="/export/projects/prastogi/kbvn/enron_contactgraph_queries"){
    ##------------#
    ## Load graph #
    ##------------#
    tic = my.time()
    graph = as.undirected(read.graph(graph.fn, format="graphml"))
    print(paste("time for loading graph=", my.time() - tic)) # 80s

    ##-------------------------#
    ## Create Adjacency Matrix #
    ##-------------------------#
    tic = my.time()
    A.matrix = as_adjacency_matrix(graph, attr="weights", sparse=TRUE)
    print(paste("time for creating adjacency=", my.time() - tic)) # 12s
    ##-------------------------------------#
    ## Check that the matrix is symmetric. #
    ##-------------------------------------#
    tic = proc.time()[3]
    stopifnot(isSymmetric(A.matrix))
    print(paste("time for Checking symmetricity=", proc.time()[3] - tic))

    ##-------------------------------------------------------------------#
    ## Precompute node and edge weight list in the hope of reducing time.#
    ##-------------------------------------------------------------------#
    tic = proc.time()[3]
    connected.node.list = list(NaN, length(V(graph)))
    edge.weights.list = list(NaN, length(V(graph)))

    ## Just this part of accessing the connected edges
    ## and the weights of connected edges is excruciatingly
    ## slow. R is for retards.
    for(state in 1:length(V(graph))){
        connected.node.idx = ego(graph, 1, nodes=state)
        connected.node.list[[state]] = connected.node.idx
        edge.weights.list[[state]] = A.matrix[connected.node.idx, state]
    }
    print(paste("time for precomputing connected node and edge weight list=",
                proc.time()[3] - tic))

    ##-----------------------------------#
    ## Create The Vertex Strength Vector #
    ##-----------------------------------#
    tic = my.time()
    graph.strength.vector = rep(NaN, length(V(graph)))
    for(state in 1:(length(V(graph)))){
        graph.strength.vector[state] = graph.strength(graph, state)
    }
    print(paste("time for creating strength=", my.time() - tic)) #

    ##------------------#
    ## Read The Queries #
    ##------------------#
    max.fields = max(count.fields(query.fn))
    queries = read.table(
        query.fn, header=FALSE, fill=TRUE, col.names=1:max.fields)
    n.queries = nrow(queries)
    print(paste("n.queries =", n.queries))

    ##------------------------------------------#
    ## for query in queries, run a random walks #
    ##------------------------------------------#
    for(qid in 1:n.queries){
        starting_points = queries[qid,-1][!is.na(queries[qid,-1])]
        n.starting_points = length(starting_points)
        ## for start in start_nodes
        print(paste("n.starting_points =", n.starting_points))
        for(starting_point_idx in 1:n.starting_points){
            start = starting_points[starting_point_idx]
            ## store a vector of counts for each start into a df
            print(paste("Starting Run", qid, starting_point_idx, start))
            tic = my.time()
            visit.vec = RW_weighted(
                graph, start, A.matrix, graph.strength.vector,
                connected.node.list, edge.weights.list,
                path.maxlength=path.maxlength, n.runs=n.runs)
            print(paste("Time for doing a walk=", my.time() - tic))
        }
    }
}
