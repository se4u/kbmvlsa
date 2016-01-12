#!/usr/bin/env Rscript
classify <- function(
    data,
    glm_families = list(binomial(link='logit'), gaussian(link='identity'))){
    nan_indices = is.nan(data$y)
    #--------------------------#
    # Create the training data #
    #--------------------------#
    train_data = data[!nan_indices,]

    #-------------------------#
    # Create the testing data #
    #-------------------------#
    test_data = data[nan_indices,]

    #------------------------------#
    # Train a number of GLM models #
    #------------------------------#

    column_names = names(data)[names(data) != 'y']
    glm_formula = paste('y ~ ', paste(column_names, collapse=' + '))
    model_list = list()
    sane.predict <- function(model, data) {
       options(warn=-1)
       prediction = predict(model, newdata = data, type="response")
       names(prediction) <- NULL
       options(warn=0)
       return(prediction)
    }
    for(i in 1:length(glm_families)){
        family = glm_families[[i]]

        model = glm(as.formula(glm_formula),
            family=family,
            data=train_data)
       test_prediction = sane.predict(model, test_data)
       write(test_prediction, '')
       train_prediction = sane.predict(model, train_data)
       write(train_prediction, '')
    }
}

# This is a file for creating
x = as.data.frame(matrix(c(1, 2, 3, 4, 5, 6, 7, 8, 9), nrow=3))
y = data.frame(y=c(NaN, 0, 1))
data = cbind(x, y)
classify(data)