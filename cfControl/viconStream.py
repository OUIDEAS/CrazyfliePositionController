from python_vicon import PyVicon
import time
import numpy as np



class viconSteam():
    def __init__(self,name):
        self.name = 'cf_1'

    def vicon_connect(self):
        print("Connecting to Vicon...")
        self.client = PyVicon()
        self.client.connect("192.168.0.197", 801)

        if not self.client.isConnected():
            print("Failed to connect to Vicon!")
            return 1
        else:
            print("Vicon connected!")
            return self.client



    def getPos(self):
        self.client.frame()
        subjects = self.client.subjects()
        trans_scale = 1000
        X = {}
        while True:
            for s in subjects:
                if (s == self.name):
                    trans = self.client.translation(s)
                    if (trans[0] == 0.0 and trans[1] == 0.0 and trans[2] == 0.0):
                        print('dead packet')
                        x_ENU = False
                        y_ENU = False
                        z_ENU = False
                        heading = False
                        X["Yaw"] = heading
                        X["x"] = x_ENU
                        X["y"] = y_ENU
                        X["z"] = z_ENU
                        return X
                    else:
                        rot = self.client.rotation(s)
                        x_ENU = trans[0] / trans_scale
                        y_ENU = trans[1] / trans_scale
                        z_ENU = trans[2] / trans_scale
                        heading = rot[2]

                    if heading < 0:
                        heading = heading + 2 * np.pi

                    if heading > np.pi:
                        heading = -(2*np.pi-heading)

                    # print(np.rad2deg(heading))


                    X["x"] = x_ENU
                    X["y"] = y_ENU
                    X["z"] = z_ENU
                    X["Yaw"] = heading
                    # print(X["x"], "\t", X["y"], "\t",X["z"])
                    if s == self.name:
                         print("X:", "{0:.3f}".format(x_ENU), "\t","Y:", "{0:.3f}".format(y_ENU), "\t","Z:", "{0:.3f}".format(z_ENU), "\t","Yaw:", "{0:.3f}".format(np.rad2deg(heading)))
                    return X


