#Send fake vicon data over zmq

import time
import numpy as np
import _thread

import threading

class fakeVicon:

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.heading = []

        time_start = time.time()

        print("Starting background data thread. . .")
        threading.Thread(target=self.backgroundData).start()

    def backgroundData(self):
        while True:
            self.x = 10*np.cos(time.time())
            self.y = 10*np.sin(time.time())
            self.z = 1
            self.heading = np.arctan2(self.y,self.x)
            time.sleep(0.001)

    def getData(self):
        print(self.x)
        return [self.x,self.y,self.z,self.heading]




