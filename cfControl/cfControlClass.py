import time
from viconStream import viconStream
import threading
from multiprocessing import Queue
from PID_CLASS import PID_CLASS
import numpy as np


class cfControlClass():
    def __init__(self,name):
        #UAV information
        self.name = name


        #Queue List
        self.vicon_queue = Queue(maxsize=100)
        self.setpoint_queue = Queue(maxsize=1)

        #Settings
        self.time_start = time.time()

        #Start the vicon thread
        self.startVicon()

        #Start the control thread
        self.startControl()



        #Temp utility functions
        # self.delayedSP()

        self.takeoffAndLand()






    def startVicon(self):
        print("Connecting to vicon stream. . .")
        self.cf_vicon = viconStream(self.name,self.vicon_queue)


    def startControl(self):
        print("Starting control thread. . .")
        self.ctrl = PID_CLASS(self.vicon_queue,self.setpoint_queue)



    def printQ(self):
        while True:
            value = self.vicon_queue.get()
            # print(self.vicon_queue.qsize())
            # print(self.vicon_queue.get())
            time.sleep(0.1)



    def delayedSP(self):

        time.sleep(5)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)

        sp = {}

        sp["x"] = 1
        sp["y"] = 2
        sp["z"] = 3
        while True:
            time.sleep(1)
            print('vicon updated at:', '{0:.3f}'.format(self.cf_vicon.update_rate),'\t','PID updating at:','{0:.3f}'.format(self.ctrl.update_rate))




    def takeoffAndLand(self):
        sp = {}
        time.sleep(5)
        print("Sending hover set-point")

        sp["x"] = 0
        sp["y"] = 0
        sp["z"] = 0.5
        self.setpoint_queue.put(sp)

        time.sleep(5)
        zs = np.linspace(0.5,0,5)
        for i in range(0,len(zs),1):
            sp["x"] = 0
            sp["y"] = 0
            sp["z"] = zs[i]
            self.setpoint_queue.put(sp)
            time.sleep(1)












