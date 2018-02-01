#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Original code from rshum19


"""
Code showing how to control the Crazyflie using the ZMQ input socket.
This code will ramp the Crazyflie motors from 25% to 45%

To work, ZMQ has to be enabled in the client configuration and the client needs
to be connected to a Crazyflie.
See https://wiki.bitcraze.io/doc:crazyflie:client:pycfclient:zmq#input_device
for the protocol documentation.
"""

import time

try:
    import zmq
except ImportError as e:
    raise Exception("ZMQ library probably not installed ({})".format(e))


# print ('disconnecting. . .')
# zmess ={
#  "version": 1,
#  "cmd": "disconnect",
#  "uri": "radio://0/80/2M"
# }


context = zmq.Context()
receiver_cmd = context.socket(zmq.REQ)
bind_addr = "tcp://127.0.0.1:{}".format(2000)
receiver_cmd.connect(bind_addr)
# receiver_cmd.send_json(zmess)
# response = receiver_cmd.recv()

time.sleep(1)

# #Connect to radio
# zmess ={
#  "version": 1,
#  "cmd": "connect",
#  "uri": "radio://0/80/2M"
# }
# receiver_cmd.send_json(zmess)
# Connection_response = receiver_cmd.recv()
# print(Connection_response)

# context = zmq.Context()
sender = context.socket(zmq.PUSH)
bind_addr = "tcp://127.0.0.1:{}".format(2004)
sender.connect(bind_addr)
#
cmdmess = {
    "version": 1,
    "ctrl": {
        "roll": 0,
        "pitch": 0,
        "yaw": 0,
        "thrust": 30
    }
}
print("starting to send control commands!")

# Unlocking thrust protection
cmdmess["ctrl"]["thrust"] = 0
sender.send_json(cmdmess)

for i in range(25, 30, 1):
    cmdmess["ctrl"]["thrust"] = i
    sender.send_json(cmdmess)
    print(i)
    time.sleep(1)

cmdmess["ctrl"]["thrust"] = 0
sender.send_json(cmdmess)
