from cfControlClass import cfControlClass
import threading
import time
import numpy as np

alt = 0.3
uav = cfControlClass(uavName='CF_1',dispUpdateRate=False,logEnabled=False,logName='scenario4',dispMessageMonitor=False)
time.sleep(2)
while uav.active:

    uav.takeoff(alt)
    time.sleep(5)

    # uav.throttleDown()
    # uav.QueueList["controlShutdown"].put('THROTTLE_DOWN')

    # uav.kill()

    uav.land()
    print('landing')
    time.sleep(3)

    uav.cf_vicon.active = False
    time.sleep(0.25)
    uav.active = False

print('dead')

for i in uav.QueueList:
    while not uav.QueueList[i].empty():
        uav.QueueList[i].get()

threads = threading.enumerate()
for i in range(0, len(threads)):
    print(threads[i].name)



