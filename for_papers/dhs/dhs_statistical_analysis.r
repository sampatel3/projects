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

data1 <- read.csv("~/Downloads/data1new.csv")
data2 <- read.csv("~/Downloads/data2new.csv")
dt <- merge(data1,data2,sort=F)
dt$Candidate <- as.character(dt$Candidate)
dt$Candidate[c(10:12)] <- "17. Prasad check newham DHS. - 7558314"
a<-data1$Swemac.simulated.DHS.TAD
b<-data1$Swemac.simulated.DHS.Prob.of.cut.out....
c<-dt$Real.DHS.TAD
reg1 <- lm(log(b) ~ a)
dt$Real.DHS.Prob.of.cut.out.... <- exp(predict.lm(object = reg1,newdata = list(a=c)))
dt$Candidate2 <- substr(dt$Candidate,1,3)
dt$Candidate2 <- factor(dt$Candidate2,levels=c("1. ","2. ","3. ","4. ","5. ","6. ","7. ","8. ","9. ","10.","11.","12.","13.","14.","15.","16.","17.","18.","19.","20.","21.","22.","23.","24.","25."),ordered = TRUE )
dt$Grade <- factor(dt$Grade,levels=c("CT1","CT2","ST3","ST4","ST5","ST6","ST7","ST8","Fellow","Consultant"),ordered = TRUE )

data1 <- merge(data1,data2[,c("Candidate","Grade")],sort=F)
names(data1) <- c("Candidate","DHS","DHS TAD","DHS Prob.of.cut.out","Grade")
names(data2) <- c("Candidate","Grade","DHS AP","DHS Lateral distance","DHS TAD","DHS Prob.of.cut.out")
data1$Group <- "Simulated"
data2$Group <- "Real"
data2$DHS <- "Real 1"
df <- rbind(data1[,c("Candidate","Grade","DHS","DHS TAD","DHS Prob.of.cut.out","Group")],data2[,c("Candidate","Grade","DHS","DHS TAD","DHS Prob.of.cut.out","Group")])
df$Candidate <- as.character(df$Candidate)
df$Candidate[c(10:12,79)] <- "17. Prasad check newham DHS. - 7558314"
df$Candidate2 <- substr(df$Candidate,1,3)
df$Candidate2 <- factor(df$Candidate2,levels=c("1. ","2. ","3. ","4. ","5. ","6. ","7. ","8. ","9. ","10.","11.","12.","13.","14.","15.","16.","17.","18.","19.","20.","21.","22.","23.","24.","25."),ordered = TRUE )
df$Grade <- factor(df$Grade,levels=c("CT1","CT2","ST3","ST4","ST5","ST6","ST7","ST8","Fellow","Consultant"),ordered = TRUE )

a<- dt$Swemac.simulated.DHS.TAD
b<- dt$Swemac.simulated.DHS.Prob.of.cut.out....
cor.test(a,b)
op <- par(cex.main = 1.5, mar = c(5, 6, 4, 5) + 0.1, mgp = c(3.5, 1, 0), cex.lab = 1.5 , font.lab = 2, cex.axis = 1.3, bty = "n", las = 1)
plot(a, b, col = "black", pch = 21, bg = "grey", cex = 2,
     xlim = c(0,35), ylim = c(0,12), ylab = "", xlab = "", axes = FALSE)
axis(1)
axis(2) 
reg1 <- lm(log(b) ~ a)
exponential <- exp(predict.lm(object = reg1,newdata = list(a=seq(0,35,1))))
lines(seq(0,35,1),exponential)
par(las = 0)
mtext("Simulated DHS TAD", side = 1, line = 2.5, cex = 1.5)
mtext("Prob of cut out (%)", side = 2, line = 3.7, cex = 1.5)
text(23, 5, "r = 0.91", cex = 1.5)

c<- dt$Real.DHS.TAD
d<- dt$Real.DHS.Prob.of.cut.out....
cor.test(c,d)
op <- par(cex.main = 1.5, mar = c(5, 6, 4, 5) + 0.1, mgp = c(3.5, 1, 0), cex.lab = 1.5 , font.lab = 2, cex.axis = 1.3, bty = "n", las = 1)
plot(c, d, col = "black", pch = 21, bg = "grey", cex = 2,
     xlim = c(0,35), ylim = c(0,12), ylab = "", xlab = "", axes = FALSE)
axis(1)
axis(2) 
reg1 <- lm(log(b) ~ a)
exponential <- exp(predict.lm(object = reg1,newdata = list(a=seq(0,35,1))))
lines(seq(0,35,1),exponential)
par(las = 0)
mtext("Real DHS TAD", side = 1, line = 2.5, cex = 1.5)
mtext("Prob of cut out (%)", side = 2, line = 3.7, cex = 1.5)
text(23, 5, "r = 0.83", cex = 1.5)

cor.test(a,c)
op <- par(cex.main = 1.5, mar = c(5, 6, 4, 5) + 0.1, mgp = c(3.5, 1, 0), cex.lab = 1.5 , font.lab = 2, cex.axis = 1.3, bty = "n", las = 1)
plot(a, c, col = "black", pch = 21, bg = "grey", cex = 2,
     xlim = c(0,35), ylim = c(0,35), ylab = "", xlab = "", axes = FALSE)
axis(1)
axis(2) 
reg1 <- lm(c ~ a)
linear <- predict.lm(object = reg1,newdata = list(a=seq(0,35,1)))
lines(seq(0,35,1),linear)
par(las = 0)
mtext("Simulated DHS TAD", side = 1, line = 2.5, cex = 1.5)
mtext("Real DHS TAD", side = 2, line = 3.7, cex = 1.5)
text(5, 18, "r = -0.0352", cex = 1.5)

boxplot(dt$Swemac.simulated.DHS.TAD~dt$Candidate2, xlab="Candidate", ylab="Simulated DHS TAD")
boxplot(dt$Swemac.simulated.DHS.TAD~dt$Grade, xlab="Grade", ylab="Simulated DHS TAD")
boxplot(dt$Real.DHS.TAD~dt$Candidate2, xlab="Candidate", ylab="Real DHS TAD")
boxplot(dt$Real.DHS.TAD~dt$Grade, xlab="Grade", ylab="Real DHS TAD")

bwplot(df$`DHS TAD`~df$Group |df$Candidate2, ylab="DHS TAD",main="Candidate")
bwplot(df$`DHS TAD`~df$Group |df$Grade, ylab="DHS TAD",main="Grade")
bwplot(df$`DHS TAD`~df$Group , ylab="DHS TAD",main="Total")
bwplot(df$`DHS TAD`~df$Candidate2 |df$Group, ylab="DHS TAD",xlab ="Candidate")
bwplot(df$`DHS TAD`~df$Grade |df$Group, ylab="DHS TAD",xlab ="Grade")

t1 <- t.test(dt$Swemac.simulated.DHS.TAD,dt$Real.DHS.TAD,paired=TRUE)$p.value
t2 <- sapply(levels(dt$Candidate2),function(x) t.test(dt$Swemac.simulated.DHS.TAD[dt$Candidate2==x],dt$Real.DHS.TAD[dt$Candidate2==x],paired=TRUE)$p.value)
t3 <- sapply(levels(dt$Grade),function(x) t.test(dt$Swemac.simulated.DHS.TAD[dt$Grade==x],dt$Real.DHS.TAD[dt$Grade==x],paired=TRUE)$p.value)

aov1 <- summary(aov(dt$Swemac.simulated.DHS.TAD~dt$Grade))[[1]][["Pr(>F)"]][[1]]
aov2 <- summary(aov(dt$Swemac.simulated.DHS.TAD~dt$Candidate2))[[1]][["Pr(>F)"]][[1]]
aov3 <- summary(aov(dt$Real.DHS.TAD~dt$Grade))[[1]][["Pr(>F)"]][[1]]
aov4 <- summary(aov(dt$Real.DHS.TAD~dt$Candidate2))[[1]][["Pr(>F)"]][[1]]

Grade <- c("CT1","CT2","ST3","ST4","ST5","ST6","ST7","ST8","Fellow","Consultant")
Level <- c("Novice","Novice","Novice","Intermediate","Intermediate","Intermediate","Intermediate","Expert","Expert","Expert")
mapping <- cbind(Grade,Level)
dt <- merge(dt,mapping,by = "Grade",sort=F)
dt$Level <- factor(dt$Level,levels=c("Novice","Intermediate","Expert"),ordered = TRUE )
df <- merge(df,mapping,by = "Grade",sort=F)
df$Level <- factor(df$Level,levels=c("Novice","Intermediate","Expert"),ordered = TRUE )

boxplot(dt$Swemac.simulated.DHS.TAD~dt$Level, xlab="Grade", ylab="Simulated DHS TAD")
boxplot(dt$Real.DHS.TAD~dt$Level, xlab="Grade", ylab="Real DHS TAD")

bwplot(df$`DHS TAD`~df$Group |df$Level, ylab="DHS TAD",main="Grade")
bwplot(df$`DHS TAD`~df$Level |df$Group, ylab="DHS TAD",xlab ="Grade")
t4 <- sapply(levels(dt$Level),function(x) t.test(dt$Swemac.simulated.DHS.TAD[dt$Level==x],dt$Real.DHS.TAD[dt$Level==x],paired=TRUE)$p.value)
aov5 <- summary(aov(dt$Swemac.simulated.DHS.TAD~dt$Level))[[1]][["Pr(>F)"]][[1]]
aov6 <- summary(aov(dt$Real.DHS.TAD~dt$Level))[[1]][["Pr(>F)"]][[1]]

t5 <- t.test(dt$Real.DHS.TAD[dt$Level=="Intermediate"],dt$Real.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("two.sided"))$p.value
t6 <- t.test(dt$Real.DHS.TAD[dt$Level=="Expert"],dt$Real.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("two.sided"))$p.value
t7 <- t.test(dt$Real.DHS.TAD[dt$Level=="Expert"],dt$Real.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("two.sided"))$p.value
t8 <- t.test(dt$Real.DHS.TAD[dt$Level=="Novice"],dt$Real.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("two.sided"))$p.value
t9 <- t.test(dt$Real.DHS.TAD[dt$Level=="Intermediate"],dt$Real.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
t10 <- t.test(dt$Real.DHS.TAD[dt$Level=="Novice"],dt$Real.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
t11 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("two.sided"))$p.value
t12 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("two.sided"))$p.value
t13 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("two.sided"))$p.value
t14 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("two.sided"))$p.value
t15 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
t16 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("two.sided"))$p.value
t<-c(t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16)

t5 <- t.test(dt$Real.DHS.TAD[dt$Level=="Intermediate"],dt$Real.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t6 <- t.test(dt$Real.DHS.TAD[dt$Level=="Expert"],dt$Real.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t7 <- t.test(dt$Real.DHS.TAD[dt$Level=="Expert"],dt$Real.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t8 <- t.test(dt$Real.DHS.TAD[dt$Level=="Novice"],dt$Real.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t9 <- t.test(dt$Real.DHS.TAD[dt$Level=="Intermediate"],dt$Real.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t10 <- t.test(dt$Real.DHS.TAD[dt$Level=="Novice"],dt$Real.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t11 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t12 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t13 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t14 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t15 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Intermediate"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t16 <- t.test(dt$Swemac.simulated.DHS.TAD[dt$Level=="Novice"],dt$Swemac.simulated.DHS.TAD[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t<-c(t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16)
t

t5 <- t.test(dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t6 <- t.test(dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Expert"],dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t7 <- t.test(dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Expert"],dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t8 <- t.test(dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Novice"],dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t9 <- t.test(dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t10 <- t.test(dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Novice"],dt$Real.DHS.Prob.of.cut.out....[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t11 <- t.test(dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t12 <- t.test(dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Expert"],dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Novice"],paired=FALSE,alternative = c("less"))$p.value
t13 <- t.test(dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Expert"],dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t14 <- t.test(dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Novice"],dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],paired=FALSE,alternative = c("less"))$p.value
t15 <- t.test(dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Intermediate"],dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t16 <- t.test(dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Novice"],dt$Swemac.simulated.DHS.Prob.of.cut.out....[dt$Level=="Expert"],paired=FALSE,alternative = c("less"))$p.value
t<-c(t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16)
t


m1<-unlist(aggregate(dt$Real.DHS.TAD, by=list(dt$Level), FUN=mean)[2])
m2<-unlist(aggregate(dt$Swemac.simulated.DHS.TAD, by=list(dt$Level), FUN=mean)[2])
m3<-unlist(aggregate(dt$Real.DHS.TAD, by=list(dt$Level), FUN=min)[2])
m4<-unlist(aggregate(dt$Swemac.simulated.DHS.TAD, by=list(dt$Level), FUN=min)[2])
m5<-unlist(aggregate(dt$Real.DHS.TAD, by=list(dt$Level), FUN=max)[2])
m6<-unlist(aggregate(dt$Swemac.simulated.DHS.TAD, by=list(dt$Level), FUN=max)[2])
m <- c(m1,m2,m3,m4,m5,m6)
m

m1<-unlist(aggregate(dt$Real.DHS.Prob.of.cut.out...., by=list(dt$Level), FUN=mean)[2])
m2<-unlist(aggregate(dt$Swemac.simulated.DHS.Prob.of.cut.out...., by=list(dt$Level), FUN=mean)[2])
m3<-unlist(aggregate(dt$Real.DHS.Prob.of.cut.out...., by=list(dt$Level), FUN=min)[2])
m4<-unlist(aggregate(dt$Swemac.simulated.DHS.Prob.of.cut.out...., by=list(dt$Level), FUN=min)[2])
m5<-unlist(aggregate(dt$Real.DHS.Prob.of.cut.out...., by=list(dt$Level), FUN=max)[2])
m6<-unlist(aggregate(dt$Swemac.simulated.DHS.Prob.of.cut.out...., by=list(dt$Level), FUN=max)[2])
m <- c(m1,m2,m3,m4,m5,m6)
m



