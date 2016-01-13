#!/usr/bin/env Rscript
### USAGE:
### x = as.data.frame(matrix(c(1, 2, 3, 4, 5, 6, 7, 8, 9), nrow=3))
### y = data.frame(y=c(NaN, 0, 1))
### my.classify.wrapper(x, y)
sane.predict <- function(model, data, warn=-1) {
    options(warn=warn)
    prediction = predict(model, newdata = data, type="response")
    names(prediction) <- NULL
    options(warn=0)
    return(prediction)
}

my.classify.wrapper <- function(
    x, y,
    glm.families=list(binomial(link='logit'), gaussian(link='identity')),
    return.everything=FALSE){
    data = cbind(x, y)

    nan_indices = is.nan(data$y)
    ##--------------------------#
    ## Create the training data #
    ##--------------------------#
    train.data = data[!nan_indices,]

    ##-------------------------#
    ## Create the testing data #
    ##-------------------------#
    test.data = data[nan_indices,]

    ##------------------------------#
    ## Train a number of GLM models #
    ##------------------------------#

    column_names = names(data)[names(data) != 'y']
    glm_formula = paste('y ~ ', paste(column_names, collapse=' + '))
    model_list = list()
    for(i in 1:length(glm.families)){
        family = glm.families[[i]]

        model = glm(as.formula(glm_formula),
            family=family,
            data=train.data)
        if(return.everything){
            return(list(model=model,
                        train.data=train.data,
                        test.data=test.data,
                        predict.fn=sane.predict))
        } else {
            test_prediction = sane.predict(model, test.data)
            write(test_prediction, '')
            train_prediction = sane.predict(model, train.data)
            write(train_prediction, '')
        }
    }
}
