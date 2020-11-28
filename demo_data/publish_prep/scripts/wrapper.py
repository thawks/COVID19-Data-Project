import numpy as np
import pandas as pd
from pathlib import Path

data_path = Path.cwd().parent / "data/Equity June-Sept FINALIZED - JUNE Data.csv"
data = pd.read_csv(data_path) # Read-in data

#%%

col_names = ['Counties','URL','FIPS','Date','Race/Ethnicity/Totals','Category','Count'] # Set new column name

a = data.columns # Grab existing column names (dates)
b = data.loc[0] # Grab race/ethnicity label

#%% Find nan values and swap to dates (in a)

daysInd = []
count = 0
count2 = 0
aPost = list(a)
bPost = list(b)
reTmp = 'nan'

for i in a:
    
    if i.find('day') != -1:
        daysTmp = i
        
    if i.find('Unnamed') != -1:
        aPost[count] = daysTmp
        
    count += 1

for j in b:
    
    if str(j).find('c') != -1:
        reTmp = j
        
    if str(j).find('nan') != -1:
        bPost[count2] =  reTmp
        
    count2 += 1
                
daysData = aPost[3:] # Get rid of unwanted column titles (leave only date data)
reData = bPost[3:] # Get rid of unwanted column titles (leave only RE data)
catData = data.loc[1][3:] # Get rid of unwanted data in front of RE categories (leave only category data)

#%% Rewrite with one for loop, a counter, and use for Counties, URL, FIPS

counties = list(data['Counties'][2:])
URL = list(data['County/State Website w/ COVID Info'][2:])
FIPS = list(data['FIPS Codes'][2:])
countiesData = []
URLdata = []
FIPSdata = []

for counterCUF in range(0,len(counties)):
    
    countiesTmp = [counties[counterCUF]]*len(daysData)
    URLtmp = [URL[counterCUF]]*len(daysData)
    FIPStmp = [FIPS[counterCUF]]*len(daysData)
    
    for counterCUF2 in range(0,len(countiesTmp)):
        countiesData.append(countiesTmp[counterCUF2])
        URLdata.append(URLtmp[counterCUF2])
        FIPSdata.append(FIPStmp[counterCUF2])

#%% Same as above section with Date, Race/Ethnicity/Totals, Category, Count, maybe include data here

daysOut = daysData*len(counties)
reDataOut = reData*len(counties)
catDataOut = list(catData)*len(counties)

dataCols = list(a)
countData = data[dataCols[3:]]
countDataOut = np.asarray(countData[2:]).flatten()

#%% Actual data list of lists same as above section (flatten)

dataOutPrep = np.asarray([countiesData,URLdata,FIPSdata,daysOut,reDataOut,catDataOut,countDataOut]).T

dataOut = pd.DataFrame(dataOutPrep,columns = col_names)
#%%
#dataOut.to_csv(Path.cwd().parent / "data/pub_equity_june-sept.csv")
