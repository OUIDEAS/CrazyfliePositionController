from cfControlClass import cfControlClass
from matplotlib import pyplot as plt
import threading
import time
from vectorField import vectorField as vf

velocity = 0.25
# Determine these values from MATLAB
m = 1
y_ratio = 0.5
k = 2.0
Ho = -3.3
theta_r = velocity / 0.35

VF = vf(m, y_ratio, k, Ho, theta_r, velocity)
VF.calcFullField()

VF.simulateDubins(velocity)
plt.pause(1)


uav = cfControlClass(uavName='CF_1',dispUpdateRate=True,logEnabled=True,logName='ExampleLog')
time.sleep(2)
while uav.active:

    uav.takeoff(0.5)
    time.sleep(5)
    uav.goto(1,1,1)
    time.sleep(5)
    uav.goto(0,0,1)
    time.sleep(5)
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



