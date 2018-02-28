from cfControlClass import cfControlClass


import threading
import time

uav = cfControlClass('CF_1',(True,'TEST2aBc4'),True)

while uav.active:
    time.sleep(0.01)
    pass

print('dead')


threads = threading.enumerate()
uav.QueueList
for i in range(0, len(threads)):
    print(threads[i].name)

