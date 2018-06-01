from cfControlClass import cfControlClass
from matplotlib import pyplot as plt
import threading
import time
from vectorField import vectorField as vf
import numpy as np
import socket
import posq
import json
import atexit


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


def getDubins2(theta,VF_heading,dt):


    # if VF_heading < 0:
    #     VF_heading = VF_heading+2*np.pi
    turnrate = 0.35
    use = True

    yaw = theta
    if use:
        if abs(theta - VF_heading) < np.pi:
            if VF_heading>theta:
                theta = theta + turnrate * dt
                # print("left turn")
            else:
                theta = theta - turnrate * dt
                print("right turn")

        else:
            if VF_heading>theta:
                theta = theta + turnrate * dt
                # print("left turn")
            else:
                theta = theta - turnrate * dt
                print("right turn")
    else:
        theta = VF_heading




    # print("yaw:",np.rad2deg(yaw),"vf:",np.rad2deg(VF_heading),"cmd heading:",np.rad2deg(theta))
    return theta



def shutdown(client_socket,addr,port):
    pkt_to_pi["left"] = 0
    pkt_to_pi["right"] = 0

    message = json.dumps(pkt_to_pi)
    client_socket.sendto(message, (addr, port))

atexit.register(shutdown)
velocity = 0.2
# Determine these values from MATLAB
m = 1
y_ratio = 0
k = 2.2
Ho = 2.9
theta_r = velocity / 0.35

VF = vf(m, y_ratio, k, Ho, theta_r, velocity)
VF.rvfWeight = 0
VF.pathH = 1
VF.calcFullField()

# VF.simulateDubins(velocity)
plt.pause(1)

alt = 0.5

uav = cfControlClass(uavName='robit',dispUpdateRate=False,logEnabled=True,logName='lm1y0Test1',dispMessageMonitor=True,usePID=False)
time.sleep(2)

#Connect to pi
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = "192.168.0.192"
port = 5555

pkt_to_pi = {}

time_start = time.time()
while uav.active:

    time.sleep(0.01)
    X = uav.QueueList["vicon"].get()
    d = 1
    x_prev = X["x"]
    y_prev = X["y"]
    z_prev = X["z"]



    time.sleep(0.1)

    VX = np.array([])
    VY = np.array([])

    dt = 0.1
    heading_old = 0
    while X["x"] < 2:
        t1 = time.time()

        while not uav.QueueList["vicon"].empty():
            X = uav.QueueList["vicon"].get()

        # print(X)
        vect = VF.getVFatXY(X["x"],X["y"])
        vf_heading = np.arctan2(vect[1],vect[0])


        vx = (x_prev-X["x"])/dt
        vy = (y_prev-X["y"])/dt

        heading = np.arctan2(vy,vx)
        # cmd_heading = getDubins(vx,vy,vf_heading,dt)


        print(np.rad2deg(vf_heading))
        print("yaw",np.rad2deg(X["yaw"]))
        cmd_heading = getDubins2(X["yaw"],vf_heading,dt)


        vf_heading = cmd_heading
        direction = 0
        old_beta = []
        vmax = 2
        base = 0.2
        t = 0

        x_cmd = d * np.cos(vf_heading)+X["x"]
        y_cmd = d * np.sin(vf_heading)+X["y"]
        XCMD = [x_cmd, y_cmd, vf_heading]

        print("vf:",np.rad2deg(vf_heading))


        # print(XCMD)
        xnow = [X["x"], X["y"], X["yaw"]]



        output = posq.step(t, xnow, XCMD, direction, old_beta, vmax, base)

        print(output[0],output[1])
        # print(xnow)

        max_speed = 100
        vl = output[0] * max_speed
        vr = output[1] * max_speed

        pkt_to_pi["left"] = int(vl)
        pkt_to_pi["right"] = int(vr)

        # print(np.rad2deg(vf_heading))
        print("sending data", pkt_to_pi)
        message = json.dumps(pkt_to_pi)
        client_socket.sendto(message.encode(),(addr,5555))


        u = np.sqrt(vx**2+vy**2)
        x_prev = X["x"]
        y_prev = X["y"]


        pkt = {
            "time": time.time() - time_start,
            "x": X["x"],
            "y": X["y"],
            "z": X["z"],
            "yaw": X["yaw"],
            "velocity": u,
            "x_sp": x_cmd,
            "y_sp": y_cmd,
            "z_sp": 0,
            "yaw_sp": 0,
        }

        uav.QueueList["dataLogger"].put_nowait(pkt)
        time.sleep(0.1)
        t2 = time.time()
        dt = t2-t1
        #print("update rate:",dt)


    shutdown(client_socket,addr,port)

    uav.logger.active = False
    time.sleep(5)

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



