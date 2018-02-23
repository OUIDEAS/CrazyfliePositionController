import time
import numpy as np
from multiprocessing import Queue
import threading


from PID_CLASS import PID_CLASS
from viconStream import viconStream
from responsePlots import responsePlots
from logger import logger

import os




class cfControlClass():
    def __init__(self,uavName='CF_1',logEnabled = (True,'Default'),plotsEnabled=True):

        self.time_start=time.time()

        #Class Settings
        self.name = uavName
        self.logEnabled = logEnabled[0]
        self.logName = logEnabled[1]

        #Queue List
        self.vicon_queue = Queue(maxsize=100)
        self.setpoint_queue = Queue(maxsize=1)
        self.logger_queue = Queue(maxsize=100)
        self.error_queue = Queue()




        #Start error monitor thread
        errorThread = threading.Thread(target=self.errorMonitor,args=())
        errorThread.daemon = True
        errorThread.start()

        #Start threads
        self.startVicon()
        self.startControl()


        # if self.logEnabled ==True:
        #     self.startLog()

        # self.printQ()

        t = threading.Thread(target=self.printQ,args=())
        t.daemon = True
        t.start()
        self.takeoffAndLand()



    def errorMonitor(self):
        while True:
            ERROR = self.error_queue.get()
            if ERROR:
                print(ERROR)





    def startVicon(self):
        print("Connecting to vicon stream. . .")
        self.cf_vicon = viconStream(self.name,self.vicon_queue,self.error_queue)


    def startControl(self):
        self.t1 = time.time()
        print("Starting control thread. . .")
        self.ctrl = PID_CLASS(self.vicon_queue,self.setpoint_queue,self.logger_queue)


    def startPlots(self):
        self.plots = responsePlots()


    def startLog(self):
        self.logger = logger(self.logger_queue,self.logName)



    def printQ(self):

        while True:
            # print('Vicon update rate:',self.cf_vicon.update_rate,'\t','PID update rate:',self.ctrl.update_rate)#,'\t','Log:',self.logger.update_rate,'\t')
            time.sleep(0.5)
            # os.system('cls')
            # print('Vicon Q:',self.vicon_queue.qsize(),'\t','SP Q:',self.setpoint_queue.qsize(),'\t','Logger Q:',self.logger_queue.qsize(),'time',str(time.time()-self.t1))



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
            pass
            # print('vicon updated at:', '{0:.3f}'.format(self.cf_vicon.update_rate),'\t','PID updating at:','{0:.3f}'.format(self.ctrl.update_rate))




    def takeoffAndLand(self):
        sp = {}
        time.sleep(5)
        print("Sending hover set-point")

        sp["x"] = 0
        sp["y"] = 0
        sp["z"] = 0.5
        self.setpoint_queue.put(sp)
        print('setpoint sent')

        while True:
            sp["z"] = time.time()
            self.setpoint_queue.put(sp)
            time.sleep(1)

        # print('done')
        # zs = np.linspace(0.5,0,5)
        # for i in range(0,len(zs),1):
        #     sp["x"] = 0
        #     sp["y"] = 0
        #     sp["z"] = zs[i]
        #     self.setpoint_queue.put(sp)
        #     time.sleep(1)












