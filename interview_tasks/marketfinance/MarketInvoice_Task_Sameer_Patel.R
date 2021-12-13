# packages
install.packages("data.table")
install.packages("ggplot2")
install.packages("plyr")
install.packages("glmnet")
install.packages("pROC")
install.packages("caret")
install.packages("foreach")
install.packages("isoreg")
install.packages("formatR")

# packages
library(data.table)
library(ggplot2)
library(glmnet)
library(pROC)
library(caret)
library(foreach)
library(plyr)
library(isoreg)
library(formatR)

### Task 1
# import data
setClass("classDate")
setAs("character","classDate", function(from) as.Date(from, format="%Y-%m-%d") )
dt = read.csv("MarketInvoice_Public_Loan_Book.csv",colClasses = c(NA,NA,NA,"classDate",NA,"classDate",NA,"classDate","classDate"))
Expected.Payment.Date = t(as.data.frame(strsplit(dt$Expected.Payment.Date,' ')))
levels(factor(Expected.Payment.Date[,2])) #always "00:00:00"
levels(factor(Expected.Payment.Date[,3])) #always "+0000"
dt$Expected.Payment.Date = as.Date(t(as.data.frame(strsplit(dt$Expected.Payment.Date,' ')))[,1],  format="%Y-%m-%d") 

# subset to trade type Standard
levels(factor(dt$Trade.Type)) #check for typo of Standard
dt2 = dt[ which(dt$Trade.Type=="Standard"),]
levels(factor(dt2$Trade.Type)) #check Standard only
dt2 = dt2[order(dt2$Seller.ID, dt2$Advance.Date),] #subset

### Task 2
# create features - expected duration
dt2$Expected.Duration = as.numeric(dt2$Expected.Payment.Date - dt2$Advance.Date)
levels(factor(dt2$Expected.Duration[dt2$Expected.Duration<0]))
#View(dt2[dt2$Expected.Duration<0,]) #Expected Payment prior to Advance Date - set to zero
dt2$Expected.Duration = ifelse(dt2$Expected.Duration<0,0,dt2$Expected.Duration)
levels(factor(dt2$Expected.Duration[dt2$Expected.Duration<0])) #check

# create features - settled trades
dt2$Settled.Ind = ifelse(!is.na(dt2$Settlement.Date),1,0)
dt2$Settled.Prior.Expected.Ind = ifelse(!is.na(dt2$Settlement.Date) & (dt2$Settlement.Date <= dt2$Expected.Payment.Date),1,0)
dt2$Settled.Trades =  unlist(
  sapply(unique(dt2$Seller.ID),function(x) 
    sapply(dt2$Advance.Date[dt2$Seller.ID == x], function(y) 
      sum(dt2$Settled.Ind[dt2$Seller.ID == x & dt2$Settlement.Date <= y & !is.na(dt2$Settlement.Date)])
    )
  )
)

dt2$Settled.Trades.Prior.Expected =  unlist(
  sapply(unique(dt2$Seller.ID),function(x) 
    sapply(dt2$Advance.Date[dt2$Seller.ID == x], function(y) 
      sum(dt2$Settled.Prior.Expected.Ind[dt2$Seller.ID == x & dt2$Settlement.Date <= y & !is.na(dt2$Settlement.Date)])
    )
  )
)
#levels(factor(dt2$Settled.Trades))
#ggplot(dt2, aes(x=Settled.Trades)) + geom_histogram(color="black", fill="white",bins=50) # Basic histogram

### Task 3
# glm1 simple logistic with k-fold CV
levels(factor(dt2$In.Arrears))
Y = ifelse(dt2$In.Arrears=="Yes",1,0) # define dependent variable
Y_hat = sum(Y)/length(Y) #0.01890802
Y_ts = aggregate(Y,by=list(format(as.Date(dt2$Advance.Date), "%Y-%m")),sum)
lengthY_ts = aggregate(Y,by=list(format(as.Date(dt2$Advance.Date), "%Y-%m")),length)
ts = cbind(Y_ts, lengthY_ts[,2],Y_hat)
colnames(ts) = c("Advance.Date","Y_sum", "obs", "Y_hat")
ts$Y_rate =ts$Y_sum/ts$obs
ggplot(data=ts, aes(x=Advance.Date, y=Y_rate, group=1)) + geom_line()+geom_point()+ geom_line(data=ts , aes(x=Advance.Date, y=Y_hat, group=1)) #check time series

X = dt2[,c("Expected.Duration","Settled.Trades")] # define feature(s)

# glm k-fold function
cv_glm_function_1 = function(X, Y, family, kfold, lambda=0, alpha=1) {
  st = Sys.time()
  kfold.list = groupKFold(group = dt2$Seller.ID,k=5)
  
  cv_glm = function(k) {
    k.trn = kfold.list[[k]]
    glm.trn = glmnet(y= Y[k.trn], x= as.matrix(X[k.trn,]), family= family, lambda=lambda, alpha=alpha)
    score = as.numeric(predict(glm.trn, newx = as.matrix(X), type='response',exact=TRUE))
    #platt_coefs = glm(Y[k.trn] ~ score[k.trn], family = "binomial")$coefficients # platt scaling
    #score = (1 / (1 + exp(-(platt_coefs[2] * score + platt_coefs[1])))) # results are not as expected
    gini.trn = 2*auc(response = Y[k.trn],predictor = score[k.trn], quiet=TRUE)-1 
    gini.tst = 2*auc(response = Y[-k.trn],predictor = score[-k.trn], quiet=TRUE)-1 
    #roc.tst = plot.roc(x = Y[-k.trn], predictor = score[-k.trn], percent=TRUE)
    
    list(score=as.matrix(score),k=k,gini.trn=gini.trn,gini.tst=gini.tst,glm.a0=glm.trn$a0,glm.beta=glm.trn$beta,glm.lambda=glm.trn$lambda)
  }
  
  list.cv = lapply(1:kfold, cv_glm)
  score = sapply(list.cv,'[[','score')
  gini.tst = sapply(list.cv,'[[','gini.tst')
  gini.trn = sapply(list.cv,'[[','gini.trn')
  a0 = sapply(list.cv,'[[','glm.a0')
  beta = sapply(list.cv,'[[','glm.beta')
  lambda = sapply(list.cv,'[[','glm.lambda')
  
  #plot.roc(x = Y, predictor = score[,1], percent=TRUE)
  #for (i in 2:kfold) {lines.roc(x= Y, predictor = score[,i], percent=TRUE)}
  print(paste0("Test Gini: ",mean(gini.tst)))
  print(paste0("Train Gini: ",mean(gini.trn)))
  
  list(score=score,gini.tst=gini.tst,gini.trn=gini.trn,a0=a0,beta=beta,lambda=lambda)
}

glm = glm(formula= Y ~ as.matrix(X), family= "binomial") # fit on full data
summary(glm)
glm1 = cv_glm_function_1(X=X, Y=Y, kfold=5, family="binomial") # run simple GLM
#print(glm1$beta) # print beta coefficients

### Task 4
# Calculate WOE
weight.of.evidence = function(X,Y) {
  evidence = NULL
  woe = NULL
  weights = rep(1,length(Y))
  Y = Y * weights
  lengthY = sum(weights)
  prior = sum(Y) / lengthY
  
  for (name in colnames(X))
  {
    col = factor(X[,name])
    colrslt = as.numeric(col)
    levelsCol = levels(col)
    prev.evdnc =  0
    for (lvl in levelsCol)
    {
      ttl = na.omit(Y[ col == lvl ])
      lengthttl = sum(na.omit( weights[ col ==lvl ] ))
      
      if (sum(ttl) < 1) evdnc = prev.evdnc # at least one bad
      else if (lengthttl < 10) evdnc =  prev.evdnc # at least ten trades
      else if (lengthttl-sum(ttl) == 0) evdnc = 1
      else evdnc = log( ((sum(ttl))/sum(Y)) / (((lengthttl-sum(ttl)))/(lengthY-sum(Y))) )
      
      colrslt[col == lvl] = evdnc
      evidence = rbind(evidence, c(name, lvl, evdnc))
      prev.evdnc = evdnc
    }
    woe = cbind(woe, colrslt)
  }
  colnames(woe) = colnames(X)
  woe[is.na(woe)] = 0
  colnames(evidence) = c("colname", "level", "woe")
  list("woe" = woe, "evidence" = evidence)
}

WOE1 = weight.of.evidence(X=X,Y=Y) # calculate WOE 
WOE.Settled.Trades = na.omit(WOE1$evidence[which(WOE1$evidence[,1]=="Settled.Trades"),]) # WOE for settled trades
Settled.Trades.Monotonic = isoreg(x = WOE.Settled.Trades[,2],y= WOE.Settled.Trades[,3]) # fit isotonic regression, output is a monotonic grouped WOE 
plot(Settled.Trades.Monotonic, main = "Settled Trades Isotonic Reg", xlab="# settled trades", ylab = "woe") # plot to see isotonic reg fit
Settled.Trades.Grouped = as.data.frame(cbind(Settled.Trades.Monotonic$x,Settled.Trades.Monotonic$y,Settled.Trades.Monotonic$yf)) # create adjusted settled trade feature - WOE and monotonic grouped WOE
colnames(Settled.Trades.Grouped) = c("Settled.Trades","Settled.Trades.WOE","Settled.Trades.Grouped")

WOE.Expected.Duration = na.omit(WOE1$evidence[which(WOE1$evidence[,1]=="Expected.Duration"),]) # WOE for expected duration
Expected.Duration.Monotonic = isoreg(x = WOE.Expected.Duration[,2],y= WOE.Expected.Duration[,3]) # fit isotonic regression, output is a monotonic grouped WOE 
plot(Expected.Duration.Monotonic, main = "Expected Duration Isotonic Reg", xlab="expected duration", ylab = "woe") # plot to see isotonic reg fit
Expected.Duration.Grouped = as.data.frame(cbind(Expected.Duration.Monotonic$x,Expected.Duration.Monotonic$y,Expected.Duration.Monotonic$yf)) # create adjusted expected duration feature - WOE and monotonic grouped WOE
colnames(Expected.Duration.Grouped) = c("Expected.Duration","Expected.Duration.WOE","Expected.Duration.Grouped")

X2 = join(x=X,y=Expected.Duration.Grouped,by="Expected.Duration",type = "left",match = "all")
X2 = join(x=X2,y=Settled.Trades.Grouped,by="Settled.Trades",type = "left",match = "all")

# glm2 with WOE
glm = glm(formula= Y ~ as.matrix(X2[,c(3,5)]), family= "binomial") # fit on full data with settled trades and expected duration WOE features
summary(glm)
glm2 = cv_glm_function_1(X=X2[,c(3,5)], Y=Y, kfold=5, family="binomial") #0.3819618
#print(glm2$beta)

# glm3 with monotonic grouping - doesn't improve model perf
glm = glm(formula= Y ~ as.matrix(X2[,c(4,6)]), family= "binomial") # fit on full data with settled trades and expected duration monotonic grouped WOE features
summary(glm)
glm3 = cv_glm_function_1(X=X2[,c(4,6)], Y=Y, kfold=5, family="binomial") #0.07532676
#print(glm3$beta)

### Task 5
# glm4 additional features  
X3 = dt2[,c("Price.Grade","Face.Value..GBP.","Advance..GBP.","Settled.Trades","Settled.Trades.Prior.Expected","Expected.Duration" )]
WOE2 = weight.of.evidence(X=X3,Y=Y)
glm = glm(formula= Y ~ as.matrix(WOE2$woe), family= "binomial") # fit on full data
summary(glm)
glm4 = cv_glm_function_1(X=WOE2$woe, Y=Y, kfold=5, family="binomial") #0.4614117

# glm5 lasso feature selection
glm.lambda.opt = cv.glmnet(y= Y, x= as.matrix(WOE2$woe), family= "binomial",type.measure="auc",nfolds=5, alpha=1)
glm.lambda = glmnet(y= Y, x= as.matrix(WOE2$woe), family= "binomial",type.measure="auc",nfolds=5, lambda=glm.lambda.opt$lambda.1se, alpha=1)#s0
glm.lambda$beta #drop Face.Value.GBP and Advance.GBP
X4 = dt2[,c("Price.Grade","Settled.Trades","Settled.Trades.Prior.Expected","Expected.Duration" )]
WOE3 = weight.of.evidence(X=X4,Y=Y)
glm5 = cv_glm_function_1(X=WOE3$woe, Y=Y, kfold=5, family="binomial") #0.460982

# Compare GLM model roc curves
roc1 = plot.roc(x = Y, predictor = rowMeans(unlist(glm1$score)), percent=TRUE, col="red",quiet=TRUE)
roc2 = lines.roc(x = Y, predictor = rowMeans(unlist(glm2$score)), percent=TRUE, col="blue",quiet=TRUE)
roc3 = lines.roc(x = Y, predictor = rowMeans(unlist(glm3$score)), percent=TRUE, col="green",quiet=TRUE)
roc4 = lines.roc(x = Y, predictor = rowMeans(unlist(glm4$score)), percent=TRUE, col="purple",quiet=TRUE)
roc5 = lines.roc(x = Y, predictor = rowMeans(unlist(glm5$score)), percent=TRUE, col="orange",quiet=TRUE)
legend("bottomright", legend=c("2-factors","2-factors WOE","2-factors WOE Isotonic","6-factors WOE","4-factors WOE"), col=c("red", "blue", "green", "purple", "orange"), lwd=5)