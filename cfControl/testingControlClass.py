from cfControlClass import cfControlClass

import threading
import time

uav = cfControlClass('CF_1',(True,'TEST2aBc4'),True)
while uav.active:

    time.sleep(1)
    print(threading.enumerate())


print('dead')
