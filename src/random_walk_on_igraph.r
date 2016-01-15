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

RW_weighted <- function(g, start,
                        path.maxlength=c(10, 25, 50),
                        n.runs=50,
                        attr.name="weights"){
    ## g is igraph object with weighted edges
    ## start is a vector of start nodes.
    ## if edges unweighted, use built in RW function
    visit=rep(NaN, length(V(g)))
    for(run in 1:n.runs){
        for(i in 1:length(start)){
            state=start[i]
            steps=0
            while(steps < path.maxlength){
                w = graph.strength(g, state)
                A <- as_adjacency_matrix(g, attr=attr.name)[state,]
                state <- sample(1:length(visit), 1, replace=FALSE, prob=A/w)
                steps = steps+1
                visit[state] <- visit[state]+1
            }
        }
    }
    return(visit)
}

main <- function(
    path.maxlength = 10,
    n.runs=50,
    graph.fn="/export/projects/prastogi/kbvn/enron_contactgraph.graphml",
    query.fn="/export/projects/prastogi/kbvn/enron_contactgraph_queries"){
    ## Load graph
    graph = as.undirected(read.graph(graph.fn, format="graphml"))

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
            RW_weighted(graph, start, path.maxlength=path.maxlength, n.runs=n.runs)
        }
    }
}
