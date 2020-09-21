#!/usr/bin/env python
# coding: utf-8

# In[52]:

### Import sys and use it to grab the command line arguments for 
### filename (should be 'name.txt' and saved in the current directory),
### IRGA baseline CO2 threshold (ppm of CO2) and IRGA measurment 
### frequency (seconds). 

import sys

filename=str(sys.argv[1])

arg_length=len(sys.argv)

if arg_length == 3:
    threshold=float(str(sys.argv[2])) #ppm co2
else:
    threshold = 1.0
    print('threshold of 1.0 ppm CO2 has been used')
    
if arg_length == 4:
    freq=float(str(sys.argv[3])) # seconds
else:
    freq=1.0
    print('measurement frequency of 1.0 seconds has been used')

# In[45]:

### Import packages and load the data.

import numpy as np
import pandas as pd

dat1=np.loadtxt(filename,dtype='str',skiprows=1)

# In[53]:

### convert the dataset to a pandas dataframe.
### restructure the time variable to be a float point number
### that increases by the frequency argument supplied in the command line.
### Begin integration by taking the trapozoidal area of each segment of CO2 
### measurements (too be grouped and summed later).

dat=pd.DataFrame(data=dat1,columns=dat1[0,0:])
#dat["area"] =pd.to_numeric(dat['area'][1:], downcast="float")
#dat["time"] =pd.to_numeric(dat['time'][1:], downcast="float")
dat["Time(H:M:S)"] = pd.to_timedelta(dat['Time(H:M:S)'][1:]).dt.total_seconds()
dat["Time(H:M:S)"] = pd.to_numeric(dat['Time(H:M:S)'][1:], downcast="float")
dat["Time(H:M:S)"] = dat["Time(H:M:S)"].astype('int64',errors='ignore')
for i in range(2,len(dat['Time(H:M:S)'][1:])):
    dat['Time(H:M:S)'][i]=dat['Time(H:M:S)'][i-1]+freq
dat["CO2(ppm)"] =pd.to_numeric(dat['CO2(ppm)'][1:], downcast="float")
dat['area']=0
for i in range(len(dat['CO2(ppm)'][1:])):
    dat['area'][i]=freq*((dat['CO2(ppm)'][i]+dat['CO2(ppm)'][i+1])/2)
dat = dat.iloc[1:]

# In[48]:

### indicate when a sample is and is not being measured

def label_on (dat):
    if dat['area'] <= threshold :
        return 0
    if dat['area'] > threshold :
        return 1


# In[49]:

### delete all rows when samples are not being measured

dat['on'] = dat.apply(lambda row: label_on(row), axis=1)
#dat.apply(lambda row: label_on(row), axis=1)
dat=dat[dat.on != 0]

# In[50]:

### use the breaks made in the continuity of the dataset to group
### rows into samples. 
### sum the trapozoidal areas for each grouped sample
### create a final dataset with the grouped sums and the original 
### timestamp from the IRGA software when that sample was injected. 

dat['count']=1+np.arange(len(dat['area']))#range(1,len(dat['area']))
dat['count2']=0
for i in range(1,len(dat['CO2(ppm)'])):
    dat['count2'].iloc[i]=dat['Time(H:M:S)'].iloc[i]-dat['Time(H:M:S)'].iloc[i-1]
dat['count2'].iloc[0]=1
dat['count3']=1
for i in range(1,len(dat['CO2(ppm)'])):
    dat['count3'].iloc[i]=dat['count2'].iloc[i]+dat['count3'].iloc[i-1]
dat['group']=dat['count3']-dat['count']
dat["Time(H:M:S)"]=pd.to_datetime(dat["Time(H:M:S)"],unit='s')
dat["Time(H:M:S)"]=dat["Time(H:M:S)"].dt.strftime('%H:%M:%S')
dat2=dat.groupby('group').first().reset_index()
dat=dat.groupby(['group'])[['area']].sum()
dat['Time(H:M:S)']=np.array(dat2["Time(H:M:S)"])

# In[26]:

# # Check that there are 3 columns for group, area, and time<br>
# # groups are random assending numbers <br>
# # areas are large positive numbers<br>
# # time is a assending clock times corresponding to when you sampled

#dat

# In[18]:

### export to excel with same file name to current directory

dat.to_excel(filename.replace('txt','xlsx'))



