install.packages("googlesheets")
install.packages("plotrix")
install.packages("data.table")
install.packages("lattice")
install.packages("survival")
install.packages("survminer")
install.packages("ggplot2")
library(googlesheets)
library(survival)
library(survminer)
library(dplyr)
library(ggplot2)
require(data.table)
library(lattice)
library(plotrix) 

# import data
setClass("myDate")
setAs("character","myDate", function(from) as.Date(from, format="%m/%d/%Y") )
dt <- read.csv("~/Downloads/Kalps/BSSH 2.12.19 - DataTidy2.csv",colClasses = c(NA,NA,NA,NA,NA,NA,NA,"myDate","myDate","myDate","integer",NA,NA))
View(dt)

# create factors
dt$PubDate3 <- ifelse(is.na(dt$PubDate),as.Date("01/01/2020", format="%m/%d/%Y"),dt$PubDate)
class(dt$PubDate3) <- "Date"
dt$Time <- dt$PubDate3-dt$Date
dt$FactorPodium <- ifelse(dt$Oral==1,"Podium","Poster")
dt$FactorConfDate <- year(dt$Date)
dt$FactorPodium <- factor(dt$FactorPodium,levels=c("Podium","Poster"),ordered = TRUE )
dt$FactorConfDate <- factor(dt$FactorConfDate,levels=c("2011","2012","2013","2014","2015"),ordered = TRUE )

# kaplan-meier dt2 published abstracts only factorPodium & by conf year
dt$Factor<-dt$FactorPodium
dt$ConfDate<-dt$FactorConfDate
fitFactor = survfit(Surv(time = dt$Time,event = dt$Published) ~ dt$Factor,weights=dt$RiskStock)
dt2 <- dt[ which(dt$Published==1 & dt$Time>=0),]
fitFactor2 = survfit(Surv(time = dt2$Time,event = dt2$Published) ~ dt2$Factor,weights=dt2$RiskStock,data=dt2)
fitFactor3 = survfit(Surv(time = dt2$Time,event = dt2$Published) ~ dt2$Factor + dt2$ConfDate,weights=dt2$RiskStock,data=dt2)

ggsurv1<-
  ggsurvplot(
  fit = fitFactor2,
  data=dt2, 
  xlab = "Time to publication (days)", 
  ylab = "Proportion of Published Abstracts",
  size = 0.5,  # change line size
  linetype = "strata", # change line type by groups
  break.time.by = 365, # break time axis by 250
  conf.int = TRUE, # Add confidence interval
  pval = TRUE # Add p-value
  ,surv.median.line = c("hv")
  ,fun = "event"
  ,palette = "npg"
  ,pval.method = TRUE
  ,pval.coord = c(2555,0.25)
  ,pval.method.coord = c(2555,0.3)
  ,risk.table = TRUE
  ,ggtheme = theme_minimal()
  ,tables.theme = theme_minimal(base_size = 9)
)
ggsurv1

ggsurv2<-
  ggsurvplot(
    fit = fitFactor3,
    data=dt2, 
    xlab = "Time to publication (days)", 
    ylab = "Proportion of Published Abstracts",
    size = 0.5,  # change line size
    linetype = "strata", # change line type by groups
    break.time.by = 730, # break time axis by 250
    conf.int = FALSE, # Add confidence interval
    ,surv.median.line = c("v")
    ,fun = "event"
    ,palette = "npg"
    ,pval.method = TRUE
    ,risk.table = TRUE
    ,ggtheme = theme_minimal()
    ,tables.theme = theme_minimal(base_size = 9)
  )
ggsurv2$plot+facet_wrap(~ConfDate)

# kaplan-meier dt2 published abstracts only factorConfDate
dt$Factor<-dt$FactorConfDate
fitFactor = survfit(Surv(time = dt$Time,event = dt$Published) ~ dt$Factor,weights=dt$RiskStock)
dt2 <- dt[ which(dt$Published==1 & dt$Time>=0),]
fitFactor2 = survfit(Surv(time = dt2$Time,event = dt2$Published) ~ dt2$Factor,weights=dt2$RiskStock)

ggsurv3<-
  ggsurvplot(
    fit = fitFactor2,
    data=dt2, 
    xlab = "Time to publication (days)", 
    ylab = "Proportion of Published Abstracts",
    size = 0.5,  # change line size
    linetype = "strata", # change line type by groups
    break.time.by = 365, # break time axis by 250
    conf.int = FALSE, # Add confidence interval
    pval = TRUE # Add p-value
    ,surv.median.line = c("hv")
    ,fun = "event"
    ,palette = "npg"
    ,pval.method = TRUE
    ,pval.coord = c(2555,0.25)
    ,pval.method.coord = c(2555,0.3)
    ,risk.table = TRUE
    ,ggtheme = theme_minimal()
    ,tables.theme = theme_minimal(base_size = 9)
  )

ggsurv3

# proportion comparison statistics and hypothesis testing factorConfDate
trials <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$RiskStock[dt$FactorConfDate==x & dt$RiskStock==1]))
events <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$Published[dt$FactorConfDate==x & dt$RiskStock==1]))
t1 <- prop.test(n=trials,x=events,correct = F)
median <- sapply(levels(dt$FactorConfDate),function(x) median(dt$PubMonths[dt$FactorConfDate==x & dt$RiskStock==1 & dt$Published==1]))
quantile <- sapply(levels(dt$FactorConfDate),function(x) quantile(dt$PubMonths[dt$FactorConfDate==x & dt$RiskStock==1 & dt$Published==1]))
median
quantile
trials
events
t1

# proportion comparison statistics and hypothesis testing factorPodium
trials <- sapply(levels(dt$FactorPodium),function(x) sum(dt$RiskStock[dt$FactorPodium==x & dt$RiskStock==1]))
events <- sapply(levels(dt$FactorPodium),function(x) sum(dt$Published[dt$FactorPodium==x & dt$RiskStock==1]))
t2 <- prop.test(n=trials,x=events,correct = F)
median <- sapply(levels(dt$FactorPodium),function(x) median(dt$PubMonths[dt$FactorPodium==x & dt$RiskStock==1 & dt$Published==1]))
quantile <- sapply(levels(dt$FactorPodium),function(x) quantile(dt$PubMonths[dt$FactorPodium==x & dt$RiskStock==1 & dt$Published==1]))
median
quantile
trials
events
t2

# proportion comparison statistics and hypothesis testing factorPodium by conf year
trialspod <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$RiskStock[dt$FactorPodium=="Podium" & dt$FactorConfDate==x & dt$RiskStock==1]))
eventspod <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$Published[dt$FactorPodium=="Podium" & dt$FactorConfDate==x & dt$RiskStock==1]))
medianpod <- sapply(levels(dt$FactorConfDate),function(x) median(dt$PubMonths[dt$FactorPodium=="Podium" & dt$FactorConfDate==x & dt$RiskStock==1 & dt$Published==1]))
quantilepod <- sapply(levels(dt$FactorConfDate),function(x) quantile(dt$PubMonths[dt$FactorPodium=="Podium" & dt$FactorConfDate==x & dt$RiskStock==1 & dt$Published==1]))
trialspos <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$RiskStock[dt$FactorPodium=="Poster" & dt$FactorConfDate==x & dt$RiskStock==1]))
eventspos <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$Published[dt$FactorPodium=="Poster" & dt$FactorConfDate==x & dt$RiskStock==1]))
medianpos <- sapply(levels(dt$FactorConfDate),function(x) median(dt$PubMonths[dt$FactorPodium=="Poster" & dt$FactorConfDate==x & dt$RiskStock==1 & dt$Published==1]))
quantilepos <- sapply(levels(dt$FactorConfDate),function(x) quantile(dt$PubMonths[dt$FactorPodium=="Poster" & dt$FactorConfDate==x & dt$RiskStock==1 & dt$Published==1]))
t3 <- sapply(levels(dt$FactorConfDate),function(x) prop.test(n=c(trialspod[x],trialspos[x]),x=c(eventspod[x],eventspos[x]),correct = F)[["p.value"]])

medianpod
quantilepod
trialspod
eventspod
medianpos
quantilepos
trialspos
eventspos
t3

# proportion comparison statistics and hypothesis testing factorConfDate (including prior published abstracts)
trials <- sapply(levels(dt$FactorConfDate),function(x) length(dt$RiskStock[dt$FactorConfDate==x]))
events <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$Published[dt$FactorConfDate==x]))
t1 <- prop.test(n=trials,x=events,correct = F)
trials
events
t1

# proportion comparison statistics and hypothesis testing factorPodium (including prior published abstracts)
trials <- sapply(levels(dt$FactorPodium),function(x) length(dt$RiskStock[dt$FactorPodium==x]))
events <- sapply(levels(dt$FactorPodium),function(x) sum(dt$Published[dt$FactorPodium==x]))
t2 <- prop.test(n=trials,x=events,correct = F)
trials
events
t2

# proportion comparison statistics and hypothesis testing factorPodiun by conf year (including prior published abstracts)
trialspod <- sapply(levels(dt$FactorConfDate),function(x) length(dt$RiskStock[dt$FactorPodium=="Podium" & dt$FactorConfDate==x ]))
eventspod <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$Published[dt$FactorPodium=="Podium" & dt$FactorConfDate==x]))
trialspos <- sapply(levels(dt$FactorConfDate),function(x) length(dt$RiskStock[dt$FactorPodium=="Poster" & dt$FactorConfDate==x ]))
eventspos <- sapply(levels(dt$FactorConfDate),function(x) sum(dt$Published[dt$FactorPodium=="Poster" & dt$FactorConfDate==x ]))
t3 <- sapply(levels(dt$FactorConfDate),function(x) prop.test(n=c(trialspod[x],trialspos[x]),x=c(eventspod[x],eventspos[x]),correct = F)[["p.value"]])
trialspod
eventspod
trialspos
eventspos
t3

