import time
import json
import socket
import numpy as np
import matplotlib.pyplot as plt
from python_vicon import PyVicon
from PointInPoly import point_in_poly
# import posq
import VFControl as VectorField
import DecayFunctions as df


def connectVicon():
    print "Connecting to Vicon. . ."
    client = PyVicon()
    client.connect("192.168.0.197", 801)    # Vicon IP and port
    time.sleep(0.5)

    if not client.isConnected():
        print "Failed to connect to Vicon!"
        return 1

    print "Vicon connected!"
    return client


def getPos(name):
    client.frame()
    subjects = client.subjects()
    mm2m = 0.001                 # Scale Vicon position data to meters
    for s in subjects:
        if s == name:
            trans = client.translation(s)
            if trans[0] == 0.0 and trans[1] == 0.0 and trans[2] == 0.0:
                print('dead packet')
                continue
            x = trans[0] * mm2m
            y = trans[1] * mm2m

            heading = client.rotation(s)[2]
            if heading < 0:
                heading = heading + 2 * np.pi

            state = [x, y, heading]
            return state


#region Initialize conection & VFs
client = connectVicon()
time.sleep(0.5)

# Establish TCP connection
class ControlPayload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)

HOST, PORT = "192.168.0.193", 9999
print "Connecting to rover. . ."
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
time.sleep(0.5)
print "Sending data. . ."

# Geofence
geofence = [(0,-1.778),(2.54,0),(2.54,-1.778),(2.54,2.286),(-1.016,1.524),(-1.778,0),(-1.016,-1.778)]

# Initialize telemetry plot
plt.figure()
plt.ion()
plt.grid()

# Posq parameters
t = 0
xNow = getPos('Rover')
direction = 0
vMax = 1
base = 0.1
oldBeta = 0

# Create navigational field
cvf = VectorField.CircleVectorField('Gradient')
cvf.mCircleRadius = 1
cvf.xc = 0
cvf.yc = 0
cvf.bUsePathFunc = False
cvf.NormVFVectors = True

# Create obstacle field
ovf = VectorField.CircleVectorField('Gradient')
ovf.mCircleRadius = 0.01
ovf.G = -1
ovf.H = -5
ovf.L = 0
ovf.xc = 1
ovf.yc = 0
ovf.bUsePathFunc = False
ovf.bNormVFVectors = True
#endregion

try:
    sock.connect((HOST, PORT))

    # Get obstacle position
    xOvf = getPos('Obstacle')
    ovf.xc = xOvf[0]
    ovf.yc = xOvf[1]

    while (True):
        # Get current positon
        xNow = getPos('Rover')
        params = VectorField.VFData()
        params.x = xNow[0]
        params.y = xNow[1]

        if not point_in_poly(xNow[0],xNow[1],geofence):
            print('Geofence breached')
            break

        # Calculate obstacle field decay
        rOVF = np.sqrt(np.square(xNow[0]-ovf.xc)+np.square(xNow[1]-ovf.yc))
        p = df.VGauss(rOVF)

        # Navigationl field component
        newCVF = cvf.GetVF_at_XY(params)
        u = newCVF.F[0]
        v = newCVF.F[1]

        # Obstacle field component
        newOVF = ovf.GetVF_at_XY(params)
        uAvoid = p*newOVF.F[0]
        vAvoid = p*newOVF.F[1]

        # Total field component
        u = u + uAvoid
        v = v + vAvoid

        # Lead rover with heading command
        d = 3 * cvf.mCircleRadius
        headingCmd = np.arctan2(v, u)
        xCmd = d * np.cos(headingCmd)
        yCmd = d * np.sin(headingCmd)
        xGoTo = [xCmd, yCmd, headingCmd]

        ### SEND THIS TO QUAD ###


        # Calculate motor speed
        # output = posq.step(t, xNow, xGoTo, direction, oldBeta, vMax, base)
        # maxSpeed = 125
        # vLeft = output[0] * maxSpeed
        # vRight = output[1] * maxSpeed
        #
        # # Send PWM commands
        # jp = json.dumps({"Left": vLeft, "Right": vRight})
        # sock.sendall(jp.encode())
        # time.sleep(0.1)

        #region Plot telemetry data
        circle = plt.Circle((ovf.xc, ovf.yc), 0.2, color='r', fill=False)
        ax = plt.gca()
        ax.add_artist(plt.scatter(xNow[0], xNow[1], c='k'))
        ax.add_artist(circle)
        plt.axis('equal')
        plt.xlabel('X Position [m]')
        plt.ylabel('Y Position [m]')

        plt.ylim(-2.5, 2.5)
        plt.xlim(-2.5, 2.5)

        plt.quiver(xNow[0], xNow[1], u, v)
        plt.pause(0.00000000000000001)
        #endregion

finally:
    sock.close()