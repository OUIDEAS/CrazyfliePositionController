from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(True,'TEST2aBc4'),True)

while uav.active:
    uav.takeoff(0.5)
    time.sleep(5)
    uav.land()
