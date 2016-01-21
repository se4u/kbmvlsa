#!/usr/bin/env Rscript
### This is an easy to use R implementation of one of our VN procedures
### The code first embeds the graph into a suitable Euclidean space and then
### runs a suitable classifier with regression to get the nomination procedure
### USAGE: R -q -e "source('VN1.R'); main(maxd=30)"
### dependencies
library("igraph")
library("mclust")
library("irlba")
library("Matrix")
source("classifier.r")
if("ssClust" %in% rownames(installed.packages()) == TRUE){
    ## line to include ssCLUST
    require(ssClust,lib.loc="/home/hltcoe/vlyzinski/...")
}

main <- function(
     graph_fn="/home/hltcoe/ngao/miniScale-2016/Kelvin/BinaryCoMentionGraph",
     vertex_feature_save_fn="/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.features",
     vertex_name_save_fn="/export/projects/prastogi/kbvn/Kelvin.BinaryCoMentionGraph.vertexnames",
     maxd=100,
     Laplacian=FALSE,
     nElbows=2,
     dim_override=1, save.vertex.names=FALSE){
    tic = proc.time()[3] 
    g <- read.graph(graph_fn, format="ncol", directed=FALSE)
    print(paste("Time taken for reading graph=", proc.time()[3] - tic)) # 45s
    vertex.names=V(g)$name    
    # Save the names of the vertices.
    if(save.vertex.names){
    	save("vertex.names", file=vertex_name_save_fn)
    }
    ## V = 270,261
    ## E = 12,526,506
    print(paste("Number of Vertices=", length(V(g)), " Number of Edges=", ecount(g)))
    ## vertex_attr(g, "name", index=10000) ":e_0b52856ecffd3d8616d3a30f676a50ad_40"
    tic = proc.time()[3] 
    w = edge_attr(g, "weight")
    print(paste("Time taken for getting weights=", proc.time()[3] - tic))

    print(paste("Maximum edge weight=", max(w)))
    tic = proc.time()[3] 
    dd <- graph.strength(
       g, vids=V(g), loops=FALSE) # Putting weights="weight" also causes error
    d = unname(dd)
    print(paste("Time taken for graph.strength=", proc.time()[3] - tic))

    tic = proc.time()[3] 
    A <- as_adjacency_matrix(g, attr="weight", edges=FALSE, names=FALSE, sparse=TRUE)
    print(paste("Time taken for getting adjacency=", proc.time()[3] - tic))

    maxd = min(maxd, min(nrow(A), ncol(A)) - 1)
    print(paste("maxd=", maxd)) # max(198489)
    tic = proc.time()[3] 
    if(Laplacian==TRUE){
        print("Doing Laplacian")
        A.svd = embed.graph.laplacian(A, d, maxd, nElbows)
	print(A.svd$d)
	dim=min(maxd, max(dim_override, getElbows(A.svd$d, nElbows)[2]))
	vertex.features = A.svd$v[,1:dim]
    }else{
        print("Doing Adjacency")
        A.svd = embed.graph.adjacency(A, d, maxd, nElbows)
	print(A.svd$d)
	dim=min(maxd, max(dim_override, getElbows(A.svd$d, nElbows)[2]))
	vertex.features = ((A.svd$v[,1:dim]) %*% diag(sqrt(A.svd$d[1:dim])))
    }
    print(paste("Time taken for embedding graph=", proc.time()[3] - tic))
    print(paste("Dimensions kept=", dim))
    ##--------------------#
    ## Save Graph Coords. #
    ##--------------------#
    out_fn = paste(vertex_feature_save_fn, "_maxd~", maxd, "_Laplacian~", Laplacian, '_SVD', sep='')
    print(out_fn)
    save("A.svd", file=out_fn)
    ## Save vertex.features
    out_fn = paste(vertex_feature_save_fn, "_maxd~", maxd, "_ProjectToSphere~FALSE", 
                   "_Laplacian~", Laplacian, "_dimkept~", dim, sep='')
    print(out_fn)
    save("vertex.features", file=out_fn)
    ## Project to Sphere and Save vertex features.
    for(i in 1:dim(vertex.features)[1]){
        vertex.features[i,] <- vertex.features[i,]/(sum(vertex.features[i,]^2)^(1/2))
    }
    out_fn = paste(vertex_feature_save_fn, "_maxd~", maxd, "_ProjectToSphere~TRUE", 
                   "_Laplacian~", Laplacian,  "_dimkept~", dim,  sep='')
    print(out_fn)
    save("vertex.features", file=out_fn)
}

embed.graph.laplacian <- function(A, d, maxd, nElbows=2){
    D <- Diagonal(nrow(A), d^{-1/2})
    A = D %*% A %*% D
    A.svd <- irlba(A, nv = maxd, right_only=TRUE, verbose=TRUE, maxit=100)
    return(A.svd)
}

embed.graph.adjacency <- function(A, d, maxd, nElbows=2){
    D <- Diagonal(nrow(A), d/nrow(A))
    A <- A+D
    A.svd <- irlba(A, nv = maxd, right_only=TRUE, verbose=TRUE, maxit=100)
    return(A.svd)
}

embed.graph <- function(A, d, maxd, Laplacian, nElbows=2){
    ## A - The adjacency/laplacian matrix.
    ## d - The graph vertex strengths.
    ## maxd - the dimension extracted from SVD
    ## nElbows - The elbows kept after elbow finding.
    ## Laplacian flag determines the way to embed A (rather its interpretation)
    ## Projecting the embedding to the sphere mitigates
    ## sparcity concerns when the graph is very sparse.
    
    return( vertex.features)
}


## the elbow finding function
getElbows <- function(dat, n = 3, threshold = FALSE, plot = TRUE) {
    ## Given a decreasingly sorted vector, return the given number of elbows
    ##
    ## Args:
    ##   dat: a input vector (e.g. a vector of standard deviations),
    ##        or a input feature matrix.
    ##   n: the number of returned elbows.
    ##   threshold: either FALSE or a number. If threshold is a number, then all
    ##   the elements in d that are not larger than the threshold will be ignored.
    ##   plot: logical. When T, it depicts a scree plot with highlighted elbows.
    ##
    ## Return:
    ##   q: a vector of length n.
    ##
    ## Reference:
    ##   Zhu, Mu and Ghodsi, Ali (2006), "Automatic dimensionality selection from
    ##   the scree plot via the use of profile likelihood", Computational
    ##   Statistics & Data Analysis, Volume 51 Issue 2, pp 918-930, November, 2006.
    ##  if (is.unsorted(-d))


    if (is.matrix(dat))
        d <- sort(apply(dat,2,sd), decreasing=TRUE)

    else
        d <- sort(dat,decreasing=TRUE)

    if (!is.logical(threshold))
        d <- d[d > threshold]

    p <- length(d)
    if (p == 0)
        stop(paste("d must have elements that are larger than the threshold ",
                   threshold), "!", sep="")

    lq <- rep(0.0, p)                     # log likelihood, function of q
    for (q in 1:p) {
        mu1 <- mean(d[1:q])
        mu2 <- mean(d[-(1:q)])              # = NaN when q = p
        sigma2 <- (sum((d[1:q] - mu1)^2) + sum((d[-(1:q)] - mu2)^2)) /
            (p - 1 - (q < p))
        lq[q] <- sum( dnorm(  d[1:q ], mu1, sqrt(sigma2), log=TRUE) ) +
            sum( dnorm(d[-(1:q)], mu2, sqrt(sigma2), log=TRUE) )
    }

    q <- which.max(lq)
    if (n > 1 && q < p) {
        q <- c(q, q + getElbows(d[(q+1):p], n-1, plot=FALSE))
    }

    if (plot==TRUE) {
        if (is.matrix(dat)) {
            sdv <- d # apply(dat,2,sd)
            plot(sdv,type="b",xlab="dim",ylab="stdev")
            points(q,sdv[q],col=2,pch=19)
        } else {
            plot(dat, type="b")
            points(q,dat[q],col=2,pch=19)
        }
    }

    return(q)
}
