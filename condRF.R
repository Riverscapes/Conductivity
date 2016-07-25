library(foreign)
install.packages("randomForest", repos="http://cran.rstudio.com/")
library(randomForest)

args = commandArgs(trailingOnly = TRUE)
if (length(args)!=3) {
  stop("You must supply all arguments.\n", call.=FALSE)
} else if (length(args)==3) {
  modelRF <- args[1]
  print(modelRF)
  wd <- args[2]
  print(wd)
  inDBF <- args[3]
  print(inDBF)
}

load(modelRF)
#load("C:\\dev\\conductivity\\rf17bCnd9.rdata")
setwd(wd)
#setwd("C:\\JL\\Testing\\Conductivity\\outputs")

ws_cond_param <- read.dbf(inDBF, as.is = FALSE)
prdCond <- predict(rf17bCnd9, newdata=ws_cond_param)
join.df <- cbind(prdCond, ws_cond_param)
pred_cond_clean <- join.df[, 1:2]
write.csv(pred_cond_clean, file="predicted_cond.csv")