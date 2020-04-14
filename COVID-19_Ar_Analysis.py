from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, FixedLocator
import numpy as nu
import pandas as pd

#Selecting data: "Confirmed", "Deaths" or "Recovered"
dataSelection = ["CONFIRMADOS", "ACTIVOS", "MUERTOS", "RECUPERADOS", "TESTEADOS"]
dataTitles = ["Confirmed", "Active", "Deaths", "Recovered", "Tested"]

fileName = "Argentina.csv"
fileCompletePath = "Argentina_Data/" + fileName

#Loading data...
databases = []
dataframe = pd.read_csv(fileCompletePath)

for i in range(len(dataSelection)):
	databases.append(dataframe[dataframe['TYPE'] == dataSelection[i]])
	del	databases[i]["TYPE"]
	databases[i] = databases[i].T
	databases[i].columns = range(databases[i].shape[1])

del dataframe

#Selecting plot scale: "linear" or "log"
plotScale = "linear"

#Selecting regions to study
#Note that the first one will be used as reference to decide periods of time to plot
regions = ["CABA", "BUENOS AIRES", "SANTA FE", "CORDOBA"]
regionsIndexes = [[],[]]
regionReference = "PROVINCIA"
quarentineStart = "20/03"
quarentineLocation = []

plotAllCountry = True #Decide if you want a final plot of total cases in Argentina.


print("###########################################")
print("    Visualization of COVID-19 Outbreak")
print("-------------------------------------------")
print("https://github.com/rvalla/COVID-19")
print("Data from argcovidapi:")
print("https://github.com/mariano22/argcovidapi")
print("------------------------------------------")
print()
print("Ploting data of ", end=" ")
print(regions, end="\r")

#Selecting data to display
startDate = "03/03" #Starting point for plotbyDate. Default: 03/03
caseCount = 10 #Starting point for plotbyOutbreak (number of confirmed cases)
outbreakDayCount = 0 #Number of days after caseCount condition is fulfiled
dataType = 0 #0 = Confirmed, 1 = Active, 2 = Deaths, 3 = Recovered
dataGuide = 0 #Data type to calculate startpoints (confirmed, active, deaths, recovered)


#Function to look for selected regions in Data Frame
def getRegionsIndexes(regions):
	indexes = [[] for c in range (len(dataSelection))]
	for d in range(len(dataSelection)):
		for i in range(len(regions)):
			for e in range(databases[d].shape[1]):
				if databases[d].loc[regionReference, e] == regions[i]:
					indexes[d].append(e)
					break
	return indexes

regionsIndexes = getRegionsIndexes(regions)

#Function to plot cases for regions by date. Use 0, 1 or 2 to select Confirmed, Deaths or Recovered
def plotbyDate(datalocation, datatype):
	figure(num=None, figsize=(8, 4), dpi=150, facecolor='w', edgecolor='k')
	for i in range(len(datalocation[datatype])):
		databases[datatype][startDate:][datalocation[datatype][i]].plot(kind='line', label=regions[i], linewidth=2.5)
	plt.title("COVID-19: " + dataTitles[datatype] + " cases since " + startDate)
	plt.legend(loc=0, prop={'size': 8})
	plt.grid(which='both', axis='both')
	plt.yscale(plotScale)
	plt.ylabel("Number of cases")
	plt.xlabel("Time in days")
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout()
	plt.show()

#Function to look for first case in each region
def regionsStartPoints(regions):
	startPoints = [[] for c in range(len(dataSelection))]
	for d in range(len(dataSelection)):
		for i in range(len(regions)):
			for e in range(databases[d].shape[0]-4):
				if databases[d].iloc[4 + e, regionsIndexes[d][i]] >= caseCount:
					startPoints[d].append(e + 4)
					break
	return startPoints

#Function to plot cases for regions since first case
def plotbyOutbreak(datalocation, datatype, dataguide):
	startPoints = regionsStartPoints(regions)
	period = databases[datatype].shape[0] - startPoints[datatype][0] - outbreakDayCount
	figure(num=None, figsize=(8, 4), dpi=150, facecolor='w', edgecolor='k')
	for i in range(len(datalocation[datatype])):
		startPoint = startPoints[dataguide][i] + outbreakDayCount
		datalist = databases[datatype][startPoint:startPoint + period][regionsIndexes[datatype][i]].values.tolist()
		plt.plot(datalist, label=regions[i], linewidth=2.5)

	plt.title("COVID-19: " + dataTitles[datatype] + " cases since number " + str(caseCount) + " " + dataTitles[dataguide])
	plt.legend(loc=0, prop={'size': 8})	
	plt.grid()
	plt.ylabel("Number of cases")
	plt.xlabel("Time in days")
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout()
	plt.show()

def getDeathRates(datalocation):
	deathRates = [[] for c in range(len(regions))]
	for r in range(len(regions)):
		confirmed = databases[0][startDate:][datalocation[0][r]].values.tolist()
		deaths = databases[2][startDate:][datalocation[1][r]].values.tolist()
		for d in range(len(confirmed)):
			if confirmed[d] > 0:
				deathRates[r].append(deaths[d]/confirmed[d])
			else:
				deathRates[r].append(0)
	return deathRates
	
def plotDeathRate(datalocation):
	deathRates = getDeathRates(regionsIndexes)
	figure(num=None, figsize=(8, 4), dpi=150, facecolor='w', edgecolor='k')
	for i in range(len(regions)):
		plt.plot(deathRates[i], label=regions[i], linewidth=2.5)
	plt.title("COVID-19: Death rate evolution since " + startDate)
	plt.legend(loc=0, prop={'size': 8})
	plt.grid(which='both', axis='both')
	plt.yscale(plotScale)
	plt.ylabel("Death ratio")
	plt.xlabel("Time in days")
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout()
	plt.show()
	
def getNewCases(datalist):
	ls = []
	ls.append(datalist[0])
	for e in range(len(datalist) - 1):
		ls.append(datalist[e+1] - datalist[e])
	return ls

def getNewCasesAv(datalist):
	ls = []
	ls.append((datalist[0] + datalist[1])/2)
	for e in range(len(datalist) - 2):
		ls.append((datalist[e+2] + datalist[e+1] + datalist[e])/3)
	index = len(datalist)
	ls.append((datalist[index-1]+datalist[index-2])/2)
	return ls

def plotNewCases(datalocation, datatype, dataguide):
	startPoints = regionsStartPoints(regions)
	period = databases[datatype].shape[0] - startPoints[datatype][0] - outbreakDayCount
	figure(num=None, figsize=(8, 4), dpi=150, facecolor='w', edgecolor='k')
	for i in range(len(datalocation[datatype])):
		startPoint = startPoints[dataguide][i] + outbreakDayCount
		datalist = databases[datatype][startPoint:startPoint + period][regionsIndexes[datatype][i]].values.tolist()
		datalistsub = getNewCases(datalist)
		plt.plot(datalistsub, label=regions[i], linewidth=2.5)
	plt.title("COVID-19: New " + dataTitles[datatype] + " cases since number " + str(caseCount) + " " + dataTitles[dataguide])
	plt.legend(loc=0, prop={'size': 8})	
	plt.grid()
	plt.ylabel("Number of new cases")
	plt.xlabel("Time in days")
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout()
	plt.show()

def plotNewCases3Av(datalocation, datatype, dataguide):
	startPoints = regionsStartPoints(regions)
	period = databases[datatype].shape[0] - startPoints[datatype][0] - outbreakDayCount
	figure(num=None, figsize=(8, 4), dpi=150, facecolor='w', edgecolor='k')
	for i in range(len(datalocation[datatype])):
		startPoint = startPoints[dataguide][i] + outbreakDayCount
		datalist = databases[datatype][startPoint:startPoint + period][regionsIndexes[datatype][i]].values.tolist()
		datalistsub = getNewCasesAv(getNewCases(datalist))
		plt.plot(datalistsub, label=regions[i], linewidth=2.5)
	plt.title("COVID-19: New " + dataTitles[datatype] + " cases trend since number " + str(caseCount) + " " + dataTitles[dataguide])
	plt.legend(loc=0, prop={'size': 8})	
	plt.grid()
	plt.ylabel("Average of new cases (3 days)")
	plt.xlabel("Time in days")
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout()
	plt.show()
	
def plotAllCountryData():
	figure = plt.figure(num=None, figsize=(7, 4.5), dpi=150, facecolor='w', edgecolor='k')
	figure.suptitle("Total cases in Argentina", fontsize=13)
	plt.subplot2grid((3, 2), (0, 0))
	for d in range(len(databases)-3):
		total = databases[d][startDate:][databases[d].shape[1] - 1].plot(kind="line", linewidth=2.0, label=dataTitles[d])
	total.legend(loc=0, prop={'size': 7})
	total.set_title("Total cases", fontsize=10)
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.subplot2grid((3, 2), (0, 1))
	for d in range(len(databases)-3):
		auxlist = databases[d][startDate:][databases[d].shape[1] - 1].values.tolist()
		ls = getNewCasesAv(getNewCases(auxlist))
		plt.plot(ls, linewidth=2.5, label=dataTitles[d])
	plt.legend(loc=0, prop={'size': 7})
	plt.title("New cases trend (3 days average)", fontsize=10)
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.subplot2grid((3, 2), (1, 0))
	deathandrecovered = databases[2][startDate:][databases[2].shape[1] - 1].plot(kind="line", linewidth=2.0, label=dataTitles[2])
	deathandrecovered.legend(loc=0, prop={'size': 7})
	deathandrecovered.set_title("Deaths", fontsize=10)
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.subplot2grid((3, 2), (2, 0))
	deathandrecovered = databases[3][startDate:][databases[3].shape[1] - 1].plot(kind="line", linewidth=2.0, label=dataTitles[3])
	deathandrecovered.legend(loc=0, prop={'size': 7})
	deathandrecovered.set_title("Recovered", fontsize=10)
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.subplot2grid((3, 2), (1, 1))
	auxlist = databases[2][startDate:][databases[2].shape[1] - 1].values.tolist()
	ls = getNewCasesAv(getNewCases(auxlist))
	plt.plot(ls, linewidth=2.5, label=dataTitles[2], color="orange")
	plt.legend(loc=0, prop={'size': 7})
	plt.title("New cases trend (deaths)", fontsize=10)
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.subplot2grid((3, 2), (2, 1))
	auxlist = databases[3][startDate:][databases[3].shape[1] - 1].values.tolist()
	ls = getNewCasesAv(getNewCases(auxlist))
	plt.plot(ls, linewidth=2.5, label=dataTitles[3], color="orange")
	plt.legend(loc=0, prop={'size': 7})
	plt.title("New cases trend (recovered)", fontsize=10)
	plt.yscale(plotScale)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout(rect=[0, 0.03, 1, 0.95])
	plt.show()

def getDuplicationTimes(datalist, type):
	newcases = getNewCases(datalist)
	duplicationtimes = []
	if type == "average":
		newcases = getNewCasesAv(newcases)
	for e in range(len(datalist)-1):
		if newcases[e+1] > 0:
			duplicationtimes.append(datalist[e]/newcases[e+1])
		else:
			duplicationtimes.append(0)
	return duplicationtimes

def plotDuplicationTimes(datalocation, datatype, dataguide):
	startPoints = regionsStartPoints(regions)
	period = databases[datatype].shape[0] - startPoints[datatype][0] - outbreakDayCount
	figure = plt.figure(num=None, figsize=(7, 4), dpi=150, facecolor='w', edgecolor='k')
	plt.subplot2grid((2, 1), (0, 0))
	for i in range(len(datalocation[datatype])):
		startPoint = startPoints[dataguide][i] + outbreakDayCount
		datalist = databases[datatype][startPoint:startPoint + period][regionsIndexes[datatype][i]].values.tolist()
		duplicationtimes = getDuplicationTimes(datalist, " ")
		plt.plot(duplicationtimes, label=regions[i], linewidth=2.0)
	plt.title("Duplication speed in days for " + dataTitles[datatype] + " cases since number " + str(caseCount) + " " + dataTitles[dataguide], fontsize=11)
	plt.legend(loc=0, prop={'size': 8})	
	plt.grid()
	plt.ylabel("Days needed\nfor cases to double", fontsize=8)
	plt.xlabel("Days", fontsize=8)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.subplot2grid((2, 1), (1, 0))
	for i in range(len(datalocation[datatype])):
		startPoint = startPoints[dataguide][i] + outbreakDayCount
		datalist = databases[datatype][startPoint:startPoint + period][regionsIndexes[datatype][i]].values.tolist()
		duplicationtimes = getDuplicationTimes(datalist, "average")
		plt.plot(duplicationtimes, label=regions[i], linewidth=2.0)
	plt.title("Duplication speed trend in days for " + dataTitles[datatype] + " cases since number " + str(caseCount) + " " + dataTitles[dataguide], fontsize=11)
	plt.legend(loc=0, prop={'size': 8})	
	plt.grid()
	plt.ylabel("Days needed\nfor cases to double", fontsize=8)
	plt.xlabel("Values for 3 days average", fontsize=8)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout(rect=[0, 0.03, 1, 1])
	plt.show()
	
def plotAllCountryDT(datatype):
	figure = plt.figure(num=None, figsize=(7, 4), dpi=150, facecolor='w', edgecolor='k')
	plt.subplot2grid((2, 1), (0, 0))
	datalist = databases[datatype][startDate:][databases[datatype].shape[1] - 1].values.tolist()
	duplicationtimes = getDuplicationTimes(datalist, " ")
	plt.bar(range(len(duplicationtimes)), duplicationtimes)
	plt.title("Argentina: Duplication speed in days for " + dataTitles[datatype] + " cases since " + str(startDate), fontsize=11)
	plt.grid()
	plt.ylabel("Days needed\nfor cases to double", fontsize=8)
	plt.xlabel("Days", fontsize=8)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.subplot2grid((2, 1), (1, 0))
	duplicationtimes = getDuplicationTimes(datalist, "average")
	plt.bar(range(len(duplicationtimes)), duplicationtimes)
	plt.title("Argentina: Duplication speed trend in days for " + dataTitles[datatype] + " cases since " + str(startDate), fontsize=11)
	plt.grid()
	plt.ylabel("Days needed\nfor cases to double", fontsize=8)
	plt.xlabel("Values for 3 days average", fontsize=8)
	plt.xticks(fontsize=6)
	plt.yticks(fontsize=6)
	plt.tight_layout(rect=[0, 0.03, 1, 1])
	plt.show()
	
plotbyDate(regionsIndexes, dataType)
plotbyOutbreak(regionsIndexes, dataType, dataGuide)
#plotNewCases(regionsIndexes, dataType, dataGuide)
plotNewCases3Av(regionsIndexes, dataType, dataGuide)
plotDeathRate(regionsIndexes)
#plotDuplicationTimes(regionsIndexes, dataType, dataGuide)
if plotAllCountry == True:
	plotAllCountryData()
	plotAllCountryDT(dataType)

print("That's all. If you want more plots, edit the code and run again.", end="\n")