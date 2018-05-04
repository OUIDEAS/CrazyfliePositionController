from cfControlClass import cfControlClass
import threading
import time


#Create an instance of the cfControlClass. The class can take several arguments
#uavName:           [str]       Name of the UAVs vicon name
#logEnabled:        [bool]      .txt log file will be created that records (x,y,z,yaw) states and (x,y,z,yaw) setpoints
#logName:           [str]       Name of the log file
#dispUpdateRate     [bool]      Displays update rate of VICON and PID threads
#dispMessageMonitor [bool]      Displays thread message (Thread states, setpoints, errors, etc)


uav = cfControlClass(uavName='CF_1',dispUpdateRate=True)



while uav.active:

    #CMD uav to takeoff to altitude 1m
    uav.takeoff(1)

    #Main script sleeps for 5 seconds. UAV will hold position until a new setpoint is rec
    time.sleep(5)

    #CMD uav to go to (x=1,y=0,z=1) and hold for 5 seconds
    uav.goto(1,0,1)
    time.sleep(5)

    #CMD uav to go to return to the origin and hold for 5 seconds
    uav.goto(0,0,1)
    time.sleep(5)

    #CMD UAV to land by sending decreasing altitude setpoints
    uav.land()
    time.sleep(2)

    #Kill vicon thread
    uav.cf_vicon.active = False
    time.sleep(0.1)

    #Kill uav class
    uav.active = False


#Empty the Queuelist so script can properly exit
for i in uav.QueueList:
    while not uav.QueueList[i].empty():
        uav.QueueList[i].get()

threads = threading.enumerate()
for i in range(0, len(threads)):
    print(threads[i].name)



