from cfControlClass import cfControlClass


import threading
import time

uav = cfControlClass('CF_1',(True,'TEST2aBc4'),True)

while uav.active:
    time.sleep(1)
    pass

print('dead')


threads = threading.enumerate()
for i in range(0, len(threads)):
    print(threads[i].name)
