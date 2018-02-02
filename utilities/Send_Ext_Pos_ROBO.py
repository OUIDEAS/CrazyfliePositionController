#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Original code from rshum19


"""
To work, ZMQ has to be enabled in the client configuration and the client needs
to be connected to a Crazyflie.
See https://wiki.bitcraze.io/doc:crazyflie:client:pycfclient:zmq#input_device
for the protocol documentation.
"""

from python_vicon import PyVicon
import time
import numpy as np

try:
    import zmq
except ImportError as e:
    raise Exception("ZMQ library probably not installed ({})".format(e))

print("Setting up socket to ext_pos . . .")
context = zmq.Context()
extpos_socket = context.socket(zmq.PUSH)
bind_addr = "tcp://127.0.0.1:{}".format(2005)
extpos_socket.connect(bind_addr)

print("Setting up socket to PID control . . .")
# context = zmq.Context()
PID_socket = context.socket(zmq.PUSH)
bind_addr_PID = "tcp://127.0.0.1:{}".format(7777)
result = PID_socket.connect(bind_addr_PID)




def vicon_connect():
    print("Connecting to Vicon...")
    client = PyVicon()
    client.connect("192.168.2.1", 801)

    if not client.isConnected():
        print("Failed to connect to Vicon!")
        return 1
    else:
        print("Vicon connected!")
        return client

def getPos(name):
    client.frame()
    subjects = client.subjects()
    trans_scale = 1000
    X = {}
    while True:
        for s in subjects:
            if (s == name):
                trans = client.translation(s)
                if (trans[0] == 0.0 and trans[1] == 0.0 and trans[2] == 0.0):
                    print('dead packet')
                    x_ENU = False
                    y_ENU = False
                    z_ENU = False
                    heading = False
                    X["heading"] = heading
                    X["x"] = x_ENU
                    X["y"] = y_ENU
                    X["z"] = z_ENU
                    return X



                else:
                    rot = client.rotation(s)
                    x_ENU = trans[0] / trans_scale
                    y_ENU = trans[1] / trans_scale
                    z_ENU = trans[2] / trans_scale
                    heading = rot[2]

                # if heading < 0:
                #     heading = heading + 2 * np.pi



                X["x"] = x_ENU
                X["y"] = y_ENU
                X["z"] = z_ENU
                X["heading"] = heading
                # print(X["x"], "\t", X["y"], "\t",X["z"])
                print("X:", "{0:.3f}".format(x_ENU), "\t","Y:", "{0:.3f}".format(y_ENU), "\t","Z:", "{0:.3f}".format(z_ENU))

                return X
            if (s == 'LF_1'):
                trans = client.translation(s)
                if (trans[0] == 0.0 and trans[1] == 0.0 and trans[2] == 0.0):
                    print('dead packet')
                    x_ENU = False
                    y_ENU = False
                    z_ENU = False
                    heading = False
                    X["heading"] = heading
                    X["x"] = x_ENU
                    X["y"] = y_ENU
                    X["z"] = z_ENU
                    return X



                else:
                    rot = client.rotation(s)
                    x_ENU = trans[0] / trans_scale
                    y_ENU = trans[1] / trans_scale
                    z_ENU = trans[2] / trans_scale
                    heading = rot[2]

                # if heading < 0:
                #     heading = heading + 2 * np.pi



                X["x"] = x_ENU
                X["y"] = y_ENU
                X["z"] = z_ENU
                X["heading"] = heading
                # print(X["x"], "\t", X["y"], "\t",X["z"])
                print(
            name,"X:", "{0:.3f}".format(x_ENU), "\t", "Y:", "{0:.3f}".format(y_ENU), "\t", "Z:", "{0:.3f}".format(z_ENU))

                return X





zmess = {
  "version": 1,
  "ext_pos":
  {
      "X": 0.0,
      "Y": 0.0,
      "Z": 0.0,
      "heading": 0.0,
      "RX": 0.0,
      "RY": 0.0,
      "RZ": 0.0,
  }
}


client = vicon_connect()
print("Connected to vicon stream")
time.sleep(1)


print("starting to send position command!")

xprev = getPos('CF_2')

while True:

    X = getPos('CF_2')
    R = getPos('MOJO_JR')

    if X["x"] is not False:
        yaw_rate = (xprev["heading"] - X["heading"])/0.1
        zmess["ext_pos"]["X"] = X["x"]
        zmess["ext_pos"]["Y"] = X["y"]
        zmess["ext_pos"]["Z"] = X["z"]
        zmess["ext_pos"]["RX"] = R["x"]
        zmess["ext_pos"]["RY"] = R["y"]
        zmess["ext_pos"]["RZ"] = R["z"]
        zmess["ext_pos"]["heading"] = yaw_rate
        # extpos_socket.send_json(zmess)

    else:
        zmess["ext_pos"]["X"] = False
        zmess["ext_pos"]["Y"] = False
        zmess["ext_pos"]["Z"] = False
        zmess["ext_pos"]["heading"] = yaw_rate
        # extpos_socket.send_json(zmess)

    PID_socket.send_json(zmess)
    
    time.sleep(0.1)
