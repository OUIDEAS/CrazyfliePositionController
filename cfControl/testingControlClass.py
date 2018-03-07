from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_3',(True,'LandTest'),True)

while uav.active:
    time.sleep(10)
    uav.QueueList["controlShutdown"].put('KILL')       #Send throttle down message to control thread

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

