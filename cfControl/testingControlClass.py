from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(False,'WaypointFollowing'),True)

while uav.active:
    uav.takeoff(0.25)
    time.sleep(5)
    uav.goto(-1,0,0.25)
    time.sleep(5)
    print("Starting VF Guidance")
    uav.startVFGuidanceManager()
    time.sleep(2)
    print("Ending VF Guidance")
    uav.vfGuidance.active = False
    time.sleep(4)
    uav.land()
    time.sleep(3)
    uav.QueueList["controlShutdown"].put('KILL')       #Send throttle down message to control thread
    time.sleep(2)

    uav.active = False

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)



