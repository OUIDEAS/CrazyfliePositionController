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

def getDubins(vx,vy,VF_heading,dt):

    turnrate = 0.35
    use = True
    if use:

        theta = np.arctan2(vy, vx)
        # print(np.rad2deg(theta))

        if abs(theta - VF_heading) < np.pi:
            if theta - VF_heading < 0:
                theta = theta + turnrate * dt
            else:
                theta = theta - turnrate * dt

        else:
            if theta - VF_heading > 0:
                theta = theta + turnrate * dt
            else:
                theta = theta - turnrate * dt
    else:
        theta = VF_heading



    # print(np.rad2deg(theta))
    return VF_heading


velocity = 0.2
# Determine these values from MATLAB
m = 1
y_ratio = 0
k = 2.2
Ho = 2.9
theta_r = velocity / 0.35

VF = vf(m, y_ratio, k, Ho, theta_r, velocity)
VF.rvfWeight = 1
VF.calcFullField()

VF.simulateDubins(velocity)
plt.pause(1)

alt = 0.5

uav = cfControlClass(uavName='CF_1',dispUpdateRate=False,logEnabled=True,logName='lm1y0Test1',dispMessageMonitor=False)
time.sleep(2)
while uav.active:
    uav.takeoff(alt)
    time.sleep(7)
    uav.goto(-1.75,0,alt)
    time.sleep(5)
    uav.goto(-1,0,alt)
    time.sleep(0.01)

    while not uav.QueueList["vicon_utility"].empty():
        uav.QueueList["vicon_utility"].get()

    time.sleep(0.01)
    X = uav.QueueList["vicon_utility"].get()
    d = 0.08
    x_prev = X["x"]
    y_prev = X["y"]
    z_prev = X["z"]

    time.sleep(0.1)
    dt = 0.1

    VX = np.array([])
    VY = np.array([])

    heading_old = 0
    while X["x"] < 1.5:

        t1 = time.time()
        X = uav.QueueList["vicon_utility"].get()
        vect = VF.getVFatXY(X["x"],X["y"])
        vf_heading = np.arctan2(vect[1],vect[0])


        vx = -(x_prev-X["x"])/dt
        vy = -(y_prev-X["y"])/dt

        if len(VX)>10:

            VX = VX[1:]
            VY = VY[1:]
            VX = np.append(VX,vx)
            VY = np.append(VY,vy)
        else:
            VX = np.append(VX,vx)
            VY = np.append(VY,vy)

        vx_average = np.mean(VX)
        vy_average = np.mean(VY)

        heading_new = np.arctan2(vy_average,vx_average)


        headingRate = (heading_new-heading_old)/dt
        heading_old = heading_new

        print(np.rad2deg(headingRate))


        # print("vx average:",vx_average,"\t","vy_average",vy_average)


        cmd_heading = getDubins(vx_average,vy_average,vf_heading,dt)
        # print(np.rad2deg(cmd_heading))


        x_cmd = X["x"] + d*np.cos(cmd_heading)
        y_cmd = X["y"] + d*np.sin(cmd_heading)

        x_go = float(x_cmd)
        y_go = float(y_cmd)
        if x_go!=0 and y_go!=0:
            uav.goto(x_go,y_go,alt)
        time.sleep(0.1)
        t2 = time.time()
        dt = t2-t1
        # print("update rate:",dt)

    uav.logger.active = False



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
    time.sleep(0.01)
    uav.active = False

print('dead')

for i in uav.QueueList:
    while not uav.QueueList[i].empty():
        uav.QueueList[i].get()

threads = threading.enumerate()
for i in range(0, len(threads)):
    print(threads[i].name)



