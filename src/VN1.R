#!/usr/bin/env Rscript
### This is an easy to use R implementation of one of our VN procedures
### The code first embeds the graph into a suitable Euclidean space and then
### runs a suitable classifier with regression to get the nomination procedure
### USAGE: R -q -e "source('VN1.R'); VN1()"
### dependencies
library("igraph")
library("mclust")
library("irlba")
if("ssClust" %in% rownames(installed.packages()) == TRUE){
    ## line to include ssCLUST
    require(ssClust,lib.loc="/home/hltcoe/vlyzinski/...")
}

VN1<-function(
    g=NaN, knownRed=c(), knownNotRed=c(), maxd=500,
    ProjectToSphere=FALSE, Laplacian=FALSE, classifier="logistic"){
    ## g is an igraph graph object
    ## check if graph has edge weights and extract the
    ## adjacency matrix of the graph
    ## classifier is:
    ## "ssgmm" for SS GMM (slow and great);
    ## "kmean" for Unsupervised K-means (fast and dirty);
    ## "randomforest" for Random Forest;
    ## "logistic" Logisitic regression
    print("Started VN1")

    if(is.nan(g)){
        g = graph.atlas(1000)
        g.was.nan = TRUE
        knownRed = c(1,7)
        knownNotRed = c(3,4)
        print("The graph was Nan. Initialized graph g= ")
        print(g)
    } else {
        g.was.nan = FALSE
    }

    if(length(edge_attr(g)$weight)==0){
        A<-as_adjacency_matrix(g)
        d<-degree(g)
    }else{
        A<-as_adjacency_matrix(g, attr="weight")
        d<-edge_attr(g)$weight
    }
    if(g.was.nan){
        print(A)
        print(d)
    }
    maxd = min(maxd, min(nrow(A), ncol(A)) - 1)
    print("maxd=")
    print(maxd)
    ## we extracted the edge list, now we embed the graph
    ## maxd is the maximum number of singular vectors you can
    ## compute, then we use an elbow finder to find a suitable
    ## dimension for the embedding
    ## set Laplacian=TRUE if you want to do Laplacian spectral embedding,
    ## otherwise, adjacency matrix is embedded directly
    if(Laplacian==TRUE){
        D<-Diagonal(length(V(g)),d^{-1/2})
        A=D%*%A%*%D
        A.svd <- irlba(A, nu = maxd, nv = maxd)
        dim=getElbows(A.svd$d,2)[2]
        A.svd.values <- A.svd$d[1:dim]
        A.svd.vectors <- A.svd$v[,1:dim]
        A.coords <- A.svd.vectors
    }else{
        D<-Diagonal(length(V(g)),d/length(V(g)))
        A<-A+D
        A.svd <- irlba(A, nu = maxd, nv = maxd)
        dim=getElbows(A.svd$d,2)[2]
        A.svd.values <- A.svd$d[1:dim]
        A.svd.vectors <- A.svd$v[,1:dim]
        A.coords <- A.svd.vectors %*% diag(sqrt(A.svd.values))
    }

    ## if the graph is very sparse, you may want to project the embedding to the sphere
    ## in order to mitigate sparcity concerns
    if(ProjectToSphere==TRUE){
        for(i in 1:dim(A.coords)[1])
            {A.coords[i,]<-A.coords[i,]/(sum(A.coords[i,]^2)^(1/2))}
    }

    ## run the classifier
    ## if not so big, use ssMclust
    if(classifier == "ssgmm"){
        n=nrow(A.coords)
        trueLabels <- rep(NA, n)
        trueLabels[knownRed] = 1
        knownCannotLink = knownNotRed
        cannotLinkWithIdx=new.env()
        for(i in knownCannotLink){
            cannotLinkWithIdx[[as.character(i)]]<-knownRed[1]
        }
        ss<-ssClust(X = A.coords,
                    knownLabels=knownRed,
                    trueLabels=trueLabels,
                    knownCannotLink=knownNotRed,
                    cannotLinkWithIdx=cannotLinkWithIdx,
                    Grange=c(2:5),
                    modelNames=c('VVV',"EEE","VII","EII"),
                    runParallel=F,
                    fracOfCores2Use=1,
                    initClassAssignments=NULL,
                    initializationStrategy = "kpp")

        ##now determine which class is "red"
        redClassNumber <- unique(ss$cl[knownRed])

        ##then process the z's and get mahalanobis distance for rankings
        redRanking <- ss$z[,redClassNumber]
        NominationScheme <- order(redRanking, decreasing = T)

    }else if(classifier == "kmeans"){
        X<-kmeans(A.coords,dim)
    }else if(classifier == "randomforest"){
        ## Create a random forest classifier.
        stop(paste("Not Implemented classifier: ", classifier))
    } else if(classifier == "logistic"){
        ## Create a logistic regression classifier.
        ## Perform the classification.
        ## Rank the outputs by class probabilities.
        labels = rep(NA, nrow(A.coords))
        labels[knownRed] = 1
        labels[knownNotRed] = 0
        source("classifier.r")
        retval = my.classify.wrapper(
            as.data.frame(A.coords),
            data.frame(y=labels),
            glm.families = list(binomial(link='logit')),
            return.everything=TRUE)
        print("Fit the model")
        model = retval$model
        train.data = retval$train.data
        test.data = retval$test.data
        predict.fn = retval$predict.fn
        train.prediction = predict.fn(model, train.data)
        train.error = get.error(model, train.data, train.prediction)
        print(train.error)
        ## test.prediction = predict.fn(model, test.data)
        ## test.error = get.error(model, test.data, test.prediction)
    } else {
        stop(paste("Not Implemented classifier: ", classifier))
    }
}

get.error <- function(model, data, prediction){
    prediction = predict(model, newdata = data, type="response")
    return(prediction == data$y)
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
