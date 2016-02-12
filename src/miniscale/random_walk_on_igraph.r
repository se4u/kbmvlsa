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
library("igraph")

RW_weighted <- function(g, start, A.matrix, graph.strength.matrix,
                        path.maxlength=c(10, 25, 50),
                        n.runs=50){
    ## g is igraph object with weighted edges
    ## start is a vector of start nodes.
    ## if edges unweighted, use built in RW function
    visit=rep(NaN, length(V(g)))
    for(i in 1:length(start)){
        w = graph.strength.matrix[state]
        A <- A.matrix[state,]
        A_by_w = A/w
        ## TODO: Sort A_by_w
        for(run in 1:n.runs){
            state=start[i]
            steps=0
            while(steps < path.maxlength){
                ## TODO: Sample using binary search based on the sorted A_by_w vector.
                state <- sample(1:length(visit), 1, replace=FALSE, prob=A_by_w)
                steps = steps+1
                visit[state] <- visit[state]+1
            }
        }
    }
    return(visit)
}

my.time <- function(){ proc.time()[3] } 

main <- function(
    path.maxlength = 10,
    n.runs=50,
    graph.fn="/export/projects/prastogi/kbvn/enron_contactgraph.graphml",
    query.fn="/export/projects/prastogi/kbvn/enron_contactgraph_queries"){
    ## Load graph
    tic = my.time()
       graph = as.undirected(read.graph(graph.fn, format="graphml"))
    print(paste("time for loading graph=", my.time() - tic)) # 80s

    tic = my.time()
       A.matrix = as_adjacency_matrix(graph, attr="weights")
    print(paste("time for creating adjacency=", my.time() - tic)) # 12s

    tic = my.time()
    graph.strength.matrix = rep(NaN, length(V(graph)))
    for(state in 1:(length(V(graph)))){
	graph.strength.matrix[state] = graph.strength(graph, state)    
    }
    print(paste("time for creating strength=", my.time() - tic)) # 

    max.fields = max(count.fields(query.fn))
    queries = read.table(query.fn, header=FALSE, fill=TRUE, col.names=1:max.fields)
    n.queries = nrow(queries)
    print(paste("n.queries =", n.queries))
    ## for query in queries
    for(qid in 1:n.queries){
        starting_points = queries[qid,-1][!is.na(queries[qid,-1])]
        n.starting_points = length(starting_points)
        ## for start in start_nodes
        print(paste("n.starting_points =", n.starting_points))
        for(starting_point_idx in 1:n.starting_points){
            start = starting_points[starting_point_idx]
            ## store a vector of counts for each start into a df
            print(paste(qid, starting_point_idx))
            visit.vec = RW_weighted(graph, start, A.matrix, graph.strength.matrix,
	                    path.maxlength=path.maxlength, 
                            n.runs=n.runs)
        }
    }
}
