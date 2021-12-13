install.packages("googlesheets")
library("googlesheets")
suppressPackageStartupMessages(library("dplyr"))
gs_copy(gs_gap(), to = "Simulated DHS comparison")
data <- gs_title("Simulated DHS comparison")
install.packages("plotrix")
install.packages("data.table")
install.packages("lattice")

require(data.table)
library(lattice)
library(plotrix) # package plotrix is needed for function "ablineclip""

#FAST programme data
dns1 <- read.csv("~/Downloads/FAST programme data - DNS1.csv")
dns2 <- read.csv("~/Downloads/FAST programme data - DNS2.csv")
level <- read.csv("~/Downloads/FAST programme data - LEVEL.csv")
dns1$ind <- "DNS1"
dns2$ind <- "DNS2"
dt<-rbind(dns1,dns2)
level$Novice.Intermediate.expert <- factor(level$Novice.Intermediate.expert,levels=c("Novice","Intermediate","Expert"),ordered = TRUE )

bwplot(dt$Overall.score..50~dt$ind, ylab="Score",main="")
bwplot(dt$Overall.score..50~dt$ind |dt$Novice.Intermediate.expert, ylab="Score",main="")
t1 <- t.test(dns2$Overall.score..50,dns1$Overall.score..50,paired=TRUE,alternative = c("greater"))$p.value
t2 <- sapply(levels(level$Novice.Intermediate.expert),function(x) t.test(dns2$Overall.score..50[dns2$Novice.Intermediate.expert==x],dns1$Overall.score..50[dns1$Novice.Intermediate.expert==x],paired=TRUE,alternative = c("greater"))$p.value)
aov1 <- summary(aov(dns1$Overall.score..50~dns1$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]
aov2 <- summary(aov(dns2$Overall.score..50~dns2$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]


bwplot(dt$Operation.time~dt$ind, ylab="Operation time",main="")
bwplot(dt$Operation.time~dt$ind |dt$Novice.Intermediate.expert, ylab="Operation time",main="")
t3 <- t.test(dns2$Operation.time,dns1$Operation.time,paired=TRUE,alternative = c("less"))$p.value
t4 <- sapply(levels(level$Novice.Intermediate.expert),function(x) t.test(dns2$Operation.time[dns2$Novice.Intermediate.expert==x],dns1$Operation.time[dns1$Novice.Intermediate.expert==x],paired=TRUE,alternative = c("less"))$p.value)
aov3 <- summary(aov(dns1$Operation.time~dns1$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]
aov4 <- summary(aov(dns2$Operation.time~dns2$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]

bwplot(dt$Femoral.cartilage.damage~dt$ind, ylab="Femoral cartilage damage",main="")
bwplot(dt$Femoral.cartilage.damage~dt$ind |dt$Novice.Intermediate.expert, ylab="Femoral cartilage damage",main="")
t5 <- t.test(dns2$Femoral.cartilage.damage,dns1$Femoral.cartilage.damage,paired=TRUE,alternative = c("less"))$p.value
t6 <- sapply(levels(level$Novice.Intermediate.expert),function(x) t.test(dns2$Femoral.cartilage.damage[dns2$Novice.Intermediate.expert==x],dns1$Femoral.cartilage.damage[dns1$Novice.Intermediate.expert==x],paired=TRUE,alternative = c("less"))$p.value)
aov5 <- summary(aov(dns1$Femoral.cartilage.damage~dns1$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]
aov6 <- summary(aov(dns2$Femoral.cartilage.damage~dns2$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]

bwplot(dt$Tibial.cartilage.damage~dt$ind, ylab="Tibial cartilage damage",main="")
bwplot(dt$Tibial.cartilage.damage~dt$ind |dt$Novice.Intermediate.expert, ylab="Tibial cartilage damage",main="")
t7 <- t.test(dns2$Tibial.cartilage.damage,dns1$Tibial.cartilage.damage,paired=TRUE,alternative = c("less"))$p.value
t8 <- sapply(levels(level$Novice.Intermediate.expert),function(x) t.test(dns2$Tibial.cartilage.damage[dns2$Novice.Intermediate.expert==x],dns1$Tibial.cartilage.damage[dns1$Novice.Intermediate.expert==x],paired=TRUE,alternative = c("less"))$p.value)
aov7 <- summary(aov(dns1$Tibial.cartilage.damage~dns1$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]
aov8 <- summary(aov(dns2$Tibial.cartilage.damage~dns2$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]

bwplot(dt$Camera.path.length~dt$ind, ylab="Camera path length",main="")
bwplot(dt$Camera.path.length~dt$ind |dt$Novice.Intermediate.expert, ylab="Camera path length",main="")
t9 <- t.test(dns2$Camera.path.length,dns1$Camera.path.length,paired=TRUE,alternative = c("less"))$p.value
t10 <- sapply(levels(level$Novice.Intermediate.expert),function(x) t.test(dns2$Camera.path.length[dns2$Novice.Intermediate.expert==x],dns1$Camera.path.length[dns1$Novice.Intermediate.expert==x],paired=TRUE,alternative = c("less"))$p.value)
aov9 <- summary(aov(dns1$Camera.path.length~dns1$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]
aov10 <- summary(aov(dns2$Camera.path.length~dns2$Novice.Intermediate.expert))[[1]][["Pr(>F)"]][[1]]

tA <- c(t1,t3,t5,t7,t9)
tG <- c(t2,t4,t6,t8,t10)
aovDNS1 <- c(aov1,aov3,aov5,aov7,aov9)
aovDNS2 <- c(aov2,aov4,aov6,aov8,aov10)


install.packages("googlesheets")
library("googlesheets")
suppressPackageStartupMessages(library("dplyr"))
gs_copy(gs_gap(), to = "Simulated DHS comparison")
data <- gs_title("Simulated DHS comparison")
install.packages("plotrix")
install.packages("data.table")
install.packages("lattice")

require(data.table)
library(lattice)
library(plotrix) # package plotrix is needed for function "ablineclip""

dt <- read.csv("~/Downloads/FAST.csv")
dt$Level <- factor(dt$Level,levels=c("Novice","Intermediate","Expert"),ordered = TRUE )
dt <- dt[-2,]
data <- dt

for (i in 5:92){
  mypath <- paste("~/Downloads/FAST Plots/plot",i, ".png", sep = "")
  png(file=mypath,width = 750, height = 750, units = "px")
  aov <- summary(aov(dt[,i]~dt$Level))[[1]][["Pr(>F)"]][[1]]
  tni <- t.test(dt[dt$Level=="Novice",i],dt[dt$Level=="Intermediate",i],paired=FALSE,alternative = c("two.sided"))$p.value
  tne <- t.test(dt[dt$Level=="Novice",i],dt[dt$Level=="Expert",i],paired=FALSE,alternative = c("two.sided"))$p.value
  tie <- t.test(dt[dt$Level=="Intermediate",i],dt[dt$Level=="Expert",i],paired=FALSE,alternative = c("two.sided"))$p.value
  print(bwplot(dt[,i]~dt$Level, ylab=colnames(dt)[i],main=paste0("AOV=",round(aov*100,4),"%",
                                                                 " T-NI=",round(tni*100,4),"%",
                                                                 " T-NE=",round(tne*100,4),"%",
                                                                 " T-IE=",round(tie*100,4),"%")))
  dev.off()
}

agg <- function(x,data) {
  dt <- data[,grepl( x , names( data ))]
  names(dt) <- gsub("LB", "",gsub("RB", "",gsub("LF", "",gsub("RF", "",names(data[,grepl( x , names( data ))])))))
  names_list <- names(dt)
  Level <- data$Level
  dt <- cbind(Level,dt)
  dtl <- reshape(dt, 
                 varying = names_list, 
                 v.names = "metric",
                 timevar = "module",
                 times = names_list, 
                 direction = "long")
  aov_list<-NULL
  tni_list<-NULL
  tne_list<-NULL
  tie_list<-NULL
  dtl$Level <- factor(dt$Level,levels=c("Novice","Intermediate","Expert"),ordered = TRUE )
  dtl$module <- factor(dtl$module,levels=unique(names_list))
  for (i in unique(names_list)){
    tmp <- dtl[dtl$module==i,]
    mypath <- paste("~/Downloads/FAST Plots/plot",x,i, ".png", sep = "")
    png(file=mypath,width = 750, height = 750, units = "px")
    aov<-summary(aov(tmp$metric~tmp$Level))[[1]][["Pr(>F)"]][[1]]
    tni <- t.test(tmp$metric[tmp$Level=="Novice"],tmp$metric[tmp$Level=="Intermediate"],paired=FALSE,alternative = c("two.sided"))$p.value
    tne <- t.test(tmp$metric[tmp$Level=="Novice"],tmp$metric[tmp$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
    tie <- t.test(tmp$metric[tmp$Level=="Intermediate"],tmp$metric[tmp$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
    aov_list<-c(aov_list,aov)
    tni_list<-c(tni_list,tni)
    tne_list<-c(tne_list,tne)
    tie_list<-c(tie_list,tie)
    print(bwplot(tmp$metric~tmp$Level, ylab=i,main=paste0("AOV:",round(aov*100,4),"%"," T-NI:",round(tni*100,4),"%"," T-NE:",round(tne*100,4),"%"," T-IE:",round(tie*100,4),"%")))
    dev.off()
  }
  aov_list <-sapply(X=aov_list,FUN = function(x){paste0("AOV:",round(x*100,4),"%")}) 
  tni_list <-sapply(X=tni_list,FUN = function(x){paste0("T-test NI:",round(x*100,4),"%")}) 
  tne_list <-sapply(X=tne_list,FUN = function(x){paste0("T-test NE:",round(x*100,4),"%")}) 
  tie_list <-sapply(X=tie_list,FUN = function(x){paste0("T-test IE:",round(x*100,4),"%")}) 
  ylab_list <- as.list(gsub("."," ",unique(names_list),fixed=TRUE))
  labels <- paste(gsub("."," ",gsub("\\d","",gsub(x,"",unique(names_list))),fixed=TRUE),"\n",aov_list)
  ylim <- as.vector(aggregate(dtl$metric, by = list(dtl$module), FUN = quantile, probs  = 0.99)[,2])
  ylim0 <- rep(0,length(levels(dtl$module)))
  ylim_list = mapply(c, ylim0, ylim, SIMPLIFY = FALSE)
  mypath <- paste("~/Downloads/FAST Plots/aplot",x, ".png", sep = "")
  png(file=mypath,width = 1000, height = 1000, units = "px")
  aov <- summary(aov(dtl$metric~dtl$Level))[[1]][["Pr(>F)"]][[1]]
  print(bwplot(dtl$metric~dtl$Level | dtl$module, ylab=NULL,ylim=ylim_list, scales = list(relation = "free"),
               main=paste0("Module: ",gsub("."," ",x,fixed=TRUE)), 
               par.settings = list(layout.heights=list(strip=3)),
               strip=strip.custom(bg="gray75",factor.levels=labels,strip.levels=rep(TRUE,length(levels(dtl$module))))))
  dev.off()
}

agg("Image.centering",data)
agg("Horizon.control",data)
agg("Telescoping",data)
agg("Periscoping",data)
agg("Trace.the.lines",data)
agg("Trace.the.curve",data)
agg("Probe.triangulation",data)
agg("Gather.the.starts",data)

data2<-data[,grepl( "\\d" , names( data ))]
names(data2) <- gsub("\\d","",gsub("Gather.the.starts","",gsub("Probe.triangulation","",
                                                               gsub("Trace.the.curve","",gsub("Trace.the.lines","",
                                                                                              gsub("Periscoping", "",gsub("Telescoping", "",gsub("Horizon.control", "",
                                                                                                                                                 gsub("Image.centering", "",names(data[,grepl( "\\d" , names( data ))]))))))))))
Level <- data$Level
data<-data2
x<-"."
dt <- data[,grepl( x , names( data ))]
names(dt) <- gsub("LB", "",gsub("RB", "",gsub("LF", "",gsub("RF", "",names( data )))))
names_list <- names(dt)
dt <- cbind(Level,dt)
dtl <- reshape(dt, 
               varying = names_list, 
               v.names = "metric",
               timevar = "module",
               times = names_list, 
               direction = "long")
aov_list<-NULL
tni_list<-NULL
tne_list<-NULL
tie_list<-NULL
dtl$Level <- factor(dt$Level,levels=c("Novice","Intermediate","Expert"),ordered = TRUE )
dtl$module <- factor(dtl$module,levels=unique(names_list))
for (i in unique(names_list)){
  tmp <- dtl[dtl$module==i,]
  mypath <- paste("~/Downloads/FAST Plots/plot",x,i, ".png", sep = "")
  png(file=mypath,width = 750, height = 750, units = "px")
  aov<-summary(aov(tmp$metric~tmp$Level))[[1]][["Pr(>F)"]][[1]]
  tni <- t.test(tmp$metric[tmp$Level=="Novice"],tmp$metric[tmp$Level=="Intermediate"],paired=FALSE,alternative = c("two.sided"))$p.value
  tne <- t.test(tmp$metric[tmp$Level=="Novice"],tmp$metric[tmp$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
  tie <- t.test(tmp$metric[tmp$Level=="Intermediate"],tmp$metric[tmp$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
  aov_list<-c(aov_list,aov)
  tni_list<-c(tni_list,tni)
  tne_list<-c(tne_list,tne)
  tie_list<-c(tie_list,tie)
  print(bwplot(tmp$metric~tmp$Level, ylab=i,main=paste0("AOV:",round(aov*100,4),"%"," T-NI:",round(tni*100,4),"%"," T-NE:",round(tne*100,4),"%"," T-IE:",round(tie*100,4),"%")))
  dev.off()
}
aov_list <-sapply(X=aov_list,FUN = function(x){paste0("AOV:",round(x*100,4),"%")}) 
tni_list <-sapply(X=tni_list,FUN = function(x){paste0("T-test NI:",round(x*100,4),"%")}) 
tne_list <-sapply(X=tne_list,FUN = function(x){paste0("T-test NE:",round(x*100,4),"%")}) 
tie_list <-sapply(X=tie_list,FUN = function(x){paste0("T-test IE:",round(x*100,4),"%")}) 
ylab_list <- as.list(gsub("."," ",unique(names_list),fixed=TRUE))
labels <- paste(gsub("."," ",unique(names_list),fixed=TRUE),"\n",aov_list)
ylim <- as.vector(aggregate(dtl$metric, by = list(dtl$module), FUN = quantile, probs  = 0.99)[,2])
ylim0 <- rep(0,length(levels(dtl$module)))
ylim_list = mapply(c, ylim0, ylim, SIMPLIFY = FALSE)
mypath <- paste("~/Downloads/FAST Plots/aplot",x, ".png", sep = "")
png(file=mypath,width = 1000, height = 1000, units = "px")
aov <- summary(aov(dtl$metric~dtl$Level))[[1]][["Pr(>F)"]][[1]]
print(bwplot(dtl$metric~dtl$Level | dtl$module, ylab=NULL,ylim=ylim_list, scales = list(relation = "free"),
             main=paste0("Module: ",gsub("."," ","Total",fixed=TRUE)), 
             par.settings = list(layout.heights=list(strip=3)),
             strip=strip.custom(bg="gray75",factor.levels=labels,strip.levels=rep(TRUE,length(levels(dtl$module))))))
dev.off()
}

agg("Time",data)
agg("Simulator.score",data)
agg("Camera.path.length",data)
agg("Camera.alignment",data)
agg("Grasper.path.length",data)
agg("Probe.path.length",data)

main=paste0("Investigating consultant grade on simulator metrics\n","Metric: ",x," AOV: ",round(aov*100,4),"%"),


