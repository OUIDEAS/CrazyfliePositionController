from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(True,'TestingVF'),True)
time.sleep(2)
while uav.active:

    uav.takeoff(0.25)
    time.sleep(5)





    uav.goto(-1.25,0,0.25)
    time.sleep(6)
    print("Starting VF Guidance")
    uav.startVFGuidanceManager()
    time.sleep(5)
    uav.goto(0,0,0.25)
    print("Ending VF Guidance")
    uav.vfGuidance.active = False
    time.sleep(1)



    uav.land()
    time.sleep(2)

    uav.cf_vicon.active = False
    time.sleep(0.1)
    uav.active = False

print('dead')

for i in uav.QueueList:
    while not uav.QueueList[i].empty():
        uav.QueueList[i].get()

threads = threading.enumerate()
for i in range(0, len(threads)):
    print(threads[i].name)



