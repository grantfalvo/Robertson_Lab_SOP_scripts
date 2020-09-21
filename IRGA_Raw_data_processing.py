#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8


# In[29]:

# ## What is your file named? <br>
# ## should be 'name.txt' and saved in the current directory

# In[ ]:





# In[52]:


import sys

#filename='9_13_20_standards.txt'
filename=str(sys.argv[1])

if sys.argv[2]:
    threshold=float(str(sys.argv[2])) #ppm co2
else:
    threshhold = 1.0
    
if sys.argv[3]:
    freq=float(str(sys.argv[3])) 
else:
    freq=1.0


# In[22]:

# In[45]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime as dt
#dat1=np.loadtxt('9_13_20 standards.txt',dtype='str')
dat1=np.loadtxt(filename,dtype='str',skiprows=1)
#dat1 = open('9_13_20 standards.txt','r')
#lines = dat1.readlines()[1:]
#dat1.close()


# In[23]:

# In[53]:


#freq=1.0
#threshhold = 1.0
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


# In[24]:

# In[48]:


def label_on (dat):
    if dat['area'] <= threshold :
        return 0
    if dat['area'] > threshold :
        return 1


# In[49]:


dat['on'] = dat.apply(lambda row: label_on(row), axis=1)
#dat.apply(lambda row: label_on(row), axis=1)
dat=dat[dat.on != 0]


# In[25]:

# In[50]:


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

# In[51]:


dat


# In[27]:

# #export to excel with same file name to current directory

# In[18]:


dat.to_excel(filename.replace('txt','xlsx'))


# In[ ]:

# In[ ]:

# In[ ]:

# In[ ]:

# In[ ]:

# In[ ]:
