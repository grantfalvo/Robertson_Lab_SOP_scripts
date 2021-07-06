#!/usr/bin/env python
# coding: utf-8

### Import sys and use it to grab the command line arguments for 
### filename (should be 'name.txt' and saved in the current directory),
### IRGA baseline CO2 threshold (ppm of CO2) and IRGA measurment 
### frequency (seconds). 

import sys

filename=str(sys.argv[1])

arg_length=len(sys.argv)
#print('number of arguments given', arg_length)

if arg_length >= 3:
    threshold=float(str(sys.argv[2])) #ppm co2
    print('threshold of',threshold,'ppm CO2 has been specified')
else:
    threshold = 1.0
    print('the default threshold of 1.0 ppm CO2 has been used')
    
if arg_length == 4:
    freq=float(str(sys.argv[3])) # seconds
    print('measurement frequency of',freq,'seconds has been specified')
else:
    freq=0.5
    print('the default measurement frequency of 0.5 seconds has been used')

### Import packages and load the data.

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None ## removes annoying warnings

dat1=np.loadtxt(filename,dtype='str',skiprows=1)

### convert the dataset to a pandas dataframe.
### restructure the time variable to be a float point number
### that increases by the frequency argument supplied in the command line.
### Begin integration by taking the trapozoidal area of each segment of CO2 
### measurements (too be grouped and summed later).

dat=pd.DataFrame(data=dat1,columns=dat1[0,0:])
dat["System_Time_(h:m:s)"] = pd.to_timedelta(dat['System_Time_(h:m:s)'][1:]).dt.total_seconds()
dat["System_Time_(h:m:s)"] = pd.to_numeric(dat['System_Time_(h:m:s)'][1:], downcast="float")
dat["System_Time_(h:m:s)"] = dat["System_Time_(h:m:s)"].astype('int64',errors='ignore')
for i in range(2,len(dat['System_Time_(h:m:s)'][1:])):
    dat['System_Time_(h:m:s)'][i]=dat['System_Time_(h:m:s)'][i-1]+freq
dat["CO₂_(µmol_mol⁻¹)"] =pd.to_numeric(dat['CO₂_(µmol_mol⁻¹)'][1:], downcast="float")
dat['area']=0
for i in range(len(dat['CO₂_(µmol_mol⁻¹)'][1:])):
    dat['area'][i]=freq*((dat['CO₂_(µmol_mol⁻¹)'][i]+dat['CO₂_(µmol_mol⁻¹)'][i+1])/2)
dat = dat.iloc[1:]

### indicate when a sample is and is not being measured

def label_on (dat):
    if dat['area']/freq <= threshold :
        return 0
    if dat['area']/freq > threshold :
        return 1

### delete all rows when samples are not being measured

dat['on'] = dat.apply(lambda row: label_on(row), axis=1)
dat=dat[dat.on != 0]

### use the breaks made in the continuity of the dataset to group
### rows into samples. 
### sum the rectangle areas for each grouped sample
### create a final dataset with the grouped sums and the original 
### timestamp from the IRGA software when that sample was injected. 

dat['count']=1+np.arange(len(dat['area']))#range(1,len(dat['area']))
dat['count2']=0
for i in range(1,len(dat['CO₂_(µmol_mol⁻¹)'])):
    dat['count2'].iloc[i]=(dat['System_Time_(h:m:s)'].iloc[i]-dat['System_Time_(h:m:s)'].iloc[i-1])/freq
dat['count2'].iloc[0]=1
dat['count3']=1
for i in range(1,len(dat['CO₂_(µmol_mol⁻¹)'])):
    dat['count3'].iloc[i]=dat['count2'].iloc[i]+dat['count3'].iloc[i-1]
dat['group']=dat['count3']-dat['count']
dat["System_Time_(h:m:s)"]=pd.to_datetime(dat["System_Time_(h:m:s)"],unit='s')
dat["System_Time_(h:m:s)"]=dat["System_Time_(h:m:s)"].dt.strftime('%H:%M:%S')
dat2=dat.groupby('group').first().reset_index()
dat4=dat.groupby(['group'])[['CO₂_(µmol_mol⁻¹)']].max()
dat=dat.groupby(['group'])[['area']].sum()
dat['System_Time_(h:m:s)']=np.array(dat2["System_Time_(h:m:s)"])
dat['max_height']=np.array(dat4["CO₂_(µmol_mol⁻¹)"])

# # Check that there are 4 columns for group, area, max_height and time
# # groups are random assending numbers 
# # areas are large positive numbers
# # max_heights are large positive numbers
# # time is a assending clock times corresponding to when you sampled

### export to excel with same file name to current directory

dat.to_excel(filename.replace('txt','xlsx'))


