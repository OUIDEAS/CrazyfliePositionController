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

alt = 1.15
uav = cfControlClass(uavName='CF',dispUpdateRate=False,logEnabled=True,logName='test',dispMessageMonitor=True)
time.sleep(2)
while uav.active:

    uav.takeoff(alt)
    time.sleep(5)
    #
    # uav.goto(-1,-1,alt)
    # time.sleep(10)
    #
    # uav.goto(-1, 1, alt)
    # time.sleep(10)

    uav.land()
    print('landing')
    time.sleep(3)

    # uav.takeoff(alt)
    # time.sleep(5)
    # uav.goto(1,0,alt)
    # time.sleep(10)
    # uav.goto(-1,0,alt)
    # time.sleep(7)
    # uav.goto(-1,1,alt)
    # time.sleep(5)
    # uav.land()
    # time.sleep(3)

    uav.cf_vicon.active = False
    time.sleep(0.25)
    uav.active = False

print('dead')
quit()
