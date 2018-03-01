from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(True,'ExampeDataLog'),True)

while uav.active:

    time.sleep(5)           #Give threads time to initialize

    dt = 2

    uav.takeoff(0.5)        #Quad takeoff to 0.5 meters
    time.sleep(2)
    uav.goto(1, 0, 0.5)
    time.sleep(dt)
    print(uav.QueueList["vicon"].get())
    # uav.goto(1, 1, 0.5)
    # time.sleep(dt)
    # uav.goto(0, 1, 0.5)
    # time.sleep(dt)
    # uav.goto(-1, 1, 0.5)
    # time.sleep(dt)
    # uav.goto(-1, 0, 0.5)
    # time.sleep(dt)
    # uav.goto(-1, -1, 0.5)
    # time.sleep(dt)
    # uav.goto(0, -1, 0.5)
    # time.sleep(dt)
    # uav.goto(1, -1, 0.5)
    # time.sleep(2)
    uav.goto(0, 0, 0.5)
    time.sleep(5)
    uav.land()
    print(uav.QueueList["vicon"].get())

    uav.QueueList["controlShutdown"].put('THROTTLE_DOWN')       #Send throttle down message to control thread

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

