from cfControlClass import cfControlClass
import threading
import time
import numpy as np



#Create an instance of the cfControlClass. The class can take several arguments
#uavName:           [str]       Name of the UAVs vicon name
#logEnabled:        [bool]      .txt log file will be created that records (x,y,z,yaw) states and (x,y,z,yaw) setpoints
#logName:           [str]       Name of the log file
#dispUpdateRate     [bool]      Displays update rate of VICON and PID threads
#dispMessageMonitor [bool]      Displays thread message (Thread states, setpoints, errors, etc)
#fakeVicon          [bool]      Fake vicon data for testing purposes


uav = cfControlClass(uavName='CF',dispUpdateRate=False,logEnabled=True,logName='demo2',dispMessageMonitor=True)
time.sleep(2)
while uav.active:

    time.sleep(30)

    uav.cf_vicon.active = False
    time.sleep(0.25)
    uav.active = False

print('dead')