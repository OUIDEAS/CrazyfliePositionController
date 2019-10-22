#   This program receives data from the Vicon System, for any object

import json
import time
import socket
from python_vicon import PyVicon
import numpy as np

#-------------------------------------------------------------------------------------------------------------
# THIS SECTION CONNECTS TO THE VICON SYSTEM

class ControlPayload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


def vicon_connect():
    print("Connecting to Vicon...")
    client1 = PyVicon()
    client1.connect("192.168.0.197", 801)

    if not client1.isConnected():
        print("Failed to connect to Vicon!")
        return 1

    print("Vicon connected!")
    return client1

#------------------------------------------------------------------------------------------------------------
#
#   units of output coordinates are in meters
#   make sure " if s == '(object name on vicon tracker)'

def getPos():
    client.frame()
    subjects = client.subjects()
    trans_scale = 1000
    if len(subjects) == 0:
        print("NO VICON SUBJECTS FOUND")
        return 0

    for s in subjects:
        if s == 'CG':
            trans = client.translation(s)
            if trans[0] == 0.0 and trans[1] == 0.0 and trans[2] == 0.0:
                print('dead packet')
                continue
            rot = client.rotation(s)
            x_enu = trans[0] / trans_scale
            y_enu = trans[1] / trans_scale
            z_enu = trans[2] / trans_scale
            head = rot[2]

            heading = np.degrees(head)

            return x_enu, y_enu, z_enu, heading

UDP_IP = "192.168.0.198"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client = vicon_connect()
time.sleep(1)

print("X, Y, Z are in meters, heading is in degrees measured CCW from the object's +y-axis.")

xnow = getPos()
print("X:" + str(xnow[0]) + "\tY:" + str(xnow[1]) + "\tZ:" + str(xnow[2]) + "\theading:" + str(xnow[3]) + "\n")

while True:
    try:
        xnow = getPos()
        print("X:" + str(xnow[0]) + "\tY:" + str(xnow[1]) + "\tZ:" + str(xnow[2]) + "\theading:" + str(xnow[3]) + "\n")

    # filehandle = open('x_coords(8_12)4.txt', 'a')
    # filehandle.write('\n' + repr(xnow[0]))
    # filehandle.close()
    #
    # filehandle = open('y_coords(8_12)4.txt', 'a')
    # filehandle.write('\n' + repr(xnow[1]))
    # filehandle.close()
    #
    # filehandle = open('z_coords(8_12)4.txt', 'a')
    # filehandle.write('\n' + repr(xnow[2]))
    # filehandle.close()
    except:
        print("exception")
