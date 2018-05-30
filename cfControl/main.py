from cfControlClass import cfControlClass
from matplotlib import pyplot as plt
import threading
import time
from vectorField import vectorField as vf
import numpy as np
#STATUS
#
# Current script will plot the simulated dubins path of a UAV avoiding an obstacle with optimized GVF.
# crazyflie can fly after plot without lag, however cannot plot real time (as expected, mpl super slow)
# Next steps are to fly in straight path with vector field and determine the UAVs velocity
#





velocity = 0.23
# Determine these values from MATLAB
m = 2
y_ratio = 0
k = 2.3
Ho = 3.2
theta_r = velocity / 0.35

VF = vf(m, y_ratio, k, Ho, theta_r, velocity)
VF.rvfWeight = 1
VF.calcFullField()

VF.simulateDubins(velocity)
plt.pause(1)

alt = 0.5

uav = cfControlClass(uavName='CF_1',dispUpdateRate=False,logEnabled=True,logName='logVelocityWithObstacle',dispMessageMonitor=True)
time.sleep(2)
while uav.active:
    uav.takeoff(alt)
    time.sleep(7)

    X = uav.QueueList["vicon_utility"].get()
    d = 0.15
    while X["x"] < 1:


        X = uav.QueueList["vicon_utility"].get()
        vect = VF.getVFatXY(X["x"],X["y"])
        vf_heading = np.arctan2(vect[1],vect[0])
        # print(np.rad2deg(vf_heading))
        x_cmd = X["x"] + d*np.cos(vf_heading)
        y_cmd = X["y"] + d*np.sin(vf_heading)

        print("x_cmd:", "\t", x_cmd,"\t","y_cmd:", "\t", y_cmd,"\t")
        x_go = float(x_cmd)
        y_go = float(y_cmd)
        uav.goto(x_go,y_go,alt)
        time.sleep(0.1)


    time.sleep(5)
    uav.goto(-1.25,0,alt)
    time.sleep(5)
    uav.land()
    print('landing')
    time.sleep(5)


    # uav.takeoff(alt)
    # time.sleep(10)
    # uav.goto(1.5,0,alt)
    # time.sleep(10)
    # uav.goto(-2,0,alt)
    # time.sleep(10)
    # uav.goto(0,0,alt)
    # time.sleep(6)
    # uav.land()
    # time.sleep(2)

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



