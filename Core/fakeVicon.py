#Send fake vicon data over zmq

import time
import numpy as np
import _thread




class fakeVicon:

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.heading = []

        time_start = time.time()

        print("Starting background data thread. . .")
        _thread.start_new_thread(self.backgroundData,())

    def backgroundData(self):
        while True:
            self.x = 10*np.cos(time.time/1000)
            self.y = 10*np.cos(time.time/1000)
            self.z = 1
            self.heading = np.arctan(self.y,self.x)



    def getData(self):

        return [self.x,self.y,self.z,self.heading]




