#!/usr/bin/env Rscript
### the sampling step would need work
### can run a bunch of these to get nMC higher
### Can you put together a quick script that takes an i-graph object
### set of starts, and walk length and nMC as its input and
### 1.  runs nMC independent random walks starting at each of the start vertices
### 2.  aggregates across all the runs, and computes the number of times each
###     state is visited across all runs
### 3.  gives as its output a list of all vertices ranked according to how often
###     they were visited across all the runs, along with the associated ranks
###     (so that ties can be seen)
### USAGE: R -q -e "source('random_walk_on_igraph.r'); main()"
library("igraph")

RW_weighted <- function(g, start,
                        path.maxlength=c(10, 25, 50),
                        n.runs=50){
    ## g is igraph object with weighted edges
    ## start is a vector of start nodes.
    ## if edges unweighted, use built in RW function
    visit=rep(NaN, length(V(g)))
    for(run in 1:nruns){
        for(i in 1:length(start)){
            state=start[i]
            steps=0
            while(steps < path.maxlength){
                w = graph.strength(g, state)
                A <- as_adjacency_matrix(g, attr="weight")[state,]
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
    ## for query in queries
    for(qid in 1:nrow){
        starting_points = queries[qid,-1][!is.na(queries[qid,-1])]
        ## for start in start_nodes
        for(starting_point_idx in 1:length(starting_points)){
            start = starting_points[starting_point_idx]
            ## store a vector of counts for each start into a df
            RW_weighted(graph, start, path.maxlength=path.maxlength, n.runs=n.runs)
        }
    }
}
