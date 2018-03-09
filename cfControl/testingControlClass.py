from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(False,'WaypointFollowing'),True)

while uav.active:
    time.sleep(5)
    uav.takeoff(0.5)
    time.sleep(5)
    uav.startWaypointManager()
    time.sleep(10)
    uav.land()
    time.sleep(3)


    # uav.takeoff(0.5)
    # time.sleep(5)
    # uav.goto(0,0,0.5)
    # time.sleep(5)
    # uav.land()
    # time.sleep(2)

    uav.QueueList["controlShutdown"].put('KILL')       #Send throttle down message to control thread

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)



