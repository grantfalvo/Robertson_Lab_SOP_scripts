import serial
import numpy as np 
import pandas as pd
import os 
from time import sleep
from datetime import datetime
import csv

### Set working directory and find initalization file
#os.chdir('/Users/falvo/Desktop/Dissertation/Soil_Resilience_Project/Soil_Resilience_Project_Github/srp_wd')
os.chdir('/home/pi/Desktop/Sun_Ra')
init_file = pd.read_excel("srp_init_file.xlsx") 
### Set working directory and find initalization file

### establish serial connection with Arduino ###
#arduino = serial.Serial('/dev/cu.usbmodem14101', 9600, timeout=1)
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
arduino.flush()
### establish serial connection with Arduino ###

### establish serial connection with IRGA and ICOS ###
#irga = serial.Serial('/dev/cu.usbserial-AO009F4C', 9600)
#icos = serial.Serial('/dev/cu.usbserial-AK08TPTC', 9600)
irga = serial.Serial('/dev/ttyUSB1', 9600)
icos = serial.Serial('/dev/ttyUSB0', 9600)
irga.flush()
icos.flush()
### establish serial connection with IRGA and ICOS ###

### IRGA and ICOS Dataloging setup
headers=init_file.columns.values
headers2=np.array(['UTC_Time','[CO2]','[N2O]'])
headers=np.append(headers,headers2)
split_word='<co2>'
irga_line=irga.readline().decode('utf-8')
icos_line=icos.readline().decode('utf-8')
sample_time_buffer=15
sample_time_limit=30
n2o_rsq=0.3
co2_rsq=0.3
### IRGA and ICOS Dataloging setup

### Define Arduino Motor Commands ### 
def Home():
    sleep(2)
    arduino.write(b"Home\n")
    reply1=arduino.readline().decode('utf-8').rstrip()
    while reply1 != 'Home':
        reply1=arduino.readline().decode('utf-8').rstrip()
    reply2=arduino.readline().decode('utf-8').rstrip()
    reply3=arduino.readline().decode('utf-8').rstrip()
    reply4=arduino.readline().decode('utf-8').rstrip()
    print('command=',reply1,'x_coord=',reply2,'y_coord=',reply3,'z_coord=',reply4)
        
def next_position(index):
    sleep(2)
    message=str(init_file['x_coordinate'][index]) + ',' + str(init_file['y_coordinate'][index])+' '+'\n'
    #print(message)
    arduino.write(b"next_position\n")
    reply=arduino.readline().decode('utf-8').rstrip()
    while reply != 'next_position':
        reply=arduino.readline().decode('utf-8').rstrip()
    arduino.write(message.encode('utf-8'))                  ## sends 'x,y'
    reply1=arduino.readline().decode('utf-8').rstrip()
    while reply1 != 'next_position':
        reply1=arduino.readline().decode('utf-8').rstrip()
    reply2=arduino.readline().decode('utf-8').rstrip()
    reply3=arduino.readline().decode('utf-8').rstrip()
    reply4=arduino.readline().decode('utf-8').rstrip()
    print('command=',reply1,'x_coord=',reply2,'y_coord=',reply3,'z_coord=',reply4)

def flush_lines():
    sleep(2)
    arduino.write(b"flush_lines\n")
    reply1=arduino.readline().decode('utf-8').rstrip()
    while reply1 != 'flush_lines':
        reply1=arduino.readline().decode('utf-8').rstrip()
    reply2=arduino.readline().decode('utf-8').rstrip()
    reply3=arduino.readline().decode('utf-8').rstrip()
    reply4=arduino.readline().decode('utf-8').rstrip()
    print('command=',reply1,'x_coord=',reply2,'y_coord=',reply3,'z_coord=',reply4)
        
def sample():
    sleep(2)
    arduino.write(b"sample\n")
    reply1=arduino.readline().decode('utf-8').rstrip()
    while reply1 != 'sample':
        reply1=arduino.readline().decode('utf-8').rstrip()
    reply2=arduino.readline().decode('utf-8').rstrip()
    reply3=arduino.readline().decode('utf-8').rstrip()
    reply4=arduino.readline().decode('utf-8').rstrip()
    print('command=',reply1,'x_coord=',reply2,'y_coord=',reply3,'z_coord=',reply4)      
### Define Arduino Motor Commands ###

### Define IRGA and ICOS datalogging function ###
def data_log(index):
    counter=0
    try:
        while (n2o_rsq < 0.5 and co2_rsq < 0.5 or counter<sample_time_buffer) == True and (counter<sample_time_limit ) == True:
            counter=counter+2
            irga_line=irga.readline().decode('utf-8')
            icos_line=icos.readline().decode('utf-8')
            irga_index=(irga_line.rfind(split_word))
            icos_index=icos_line.index(',')
            irga_string=irga_line[irga_index+5:irga_index+16]
            icos_string=icos_line[icos_index+4:icos_index+16]
            if irga_string[-2]=='e':
                if icos_string[-2]=='0':
                    irga_data=round(np.float32(irga_string),3)
                    icos_data=round(1000*np.float32(icos_string),3)
                    with open("test_data.csv","a") as f:
                        writer = csv.writer(f,delimiter=",")
                        writer.writerow([init_file['jar_id'][index],datetime.utcnow(),irga_data,icos_data])
    except KeyboardInterrupt:
        pass           
                
### Define IRGA and ICOS datalogging function ###


Home()
test_array=np.arange(0,96,1)
#test_array=np.array([90,91,92])
for i in test_array:
    flush_lines()
    print('----------------------------------------')
    print('x_coord=',init_file['x_coordinate'][i],'y_coord=',init_file['y_coordinate'][i])
    print('----------------------------------------')
    next_position(i)
    print('----------------------------------------')
    print('x_coord=',init_file['x_coordinate'][i],'y_coord=',init_file['y_coordinate'][i])
    print('----------------------------------------')
    sample()
    data_log(i)
    print('----------------------------------------')
    print('x_coord=',init_file['x_coordinate'][i],'y_coord=',init_file['y_coordinate'][i])
    print('----------------------------------------')

flush_lines()



