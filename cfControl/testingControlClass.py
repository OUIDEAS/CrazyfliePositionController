from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(True,'TEST2aBc4'),True)

dt = 0.75
while uav.active:


    uav.takeoff(0.5)
    time.sleep(3)

    uav.goto(1,0,0.5)
    time.sleep(dt)

    uav.goto(1,1,0.5)
    time.sleep(dt)

    uav.goto(0, 1, 0.5)
    time.sleep(dt)

    uav.goto(-1, 1, 0.5)
    time.sleep(dt)

    uav.goto(-1, 0, 0.5)
    time.sleep(dt)

    uav.goto(-1, -1, 0.5)
    time.sleep(dt)

    uav.goto(0, -1, 0.5)
    time.sleep(dt)

    uav.goto(1, -1, 0.5)
    time.sleep(dt)

    uav.goto(0,0,0.5)
    time.sleep(2)

    uav.land()
