import time
import numpy as np
from multiprocessing import Queue
import threading

from PID_CLASS import PID_CLASS
from viconStream import viconStream
# from responsePlots import responsePlots
from logger import logger


class cfControlClass():
    def __init__(self,uavName='CF_1',logEnabled = (True,'Default'),plotsEnabled=True):

        self.time_start=time.time()
        self.printUpdateRate = False
        self.active = True
        #Class Settings
        self.name = uavName
        self.logEnabled = logEnabled[0]
        self.logName = logEnabled[1]

        #Queue Dictionary
        self.QueueList = {}
        self.QueueList["vicon"] = Queue(maxsize=100)
        self.QueueList["sp"] = Queue(maxsize=10)
        self.QueueList["log"] = Queue(maxsize=100)
        self.QueueList["error"] = Queue()
        self.QueueList["kill"] = Queue()

        #Start error monitor thread
        errorThread = threading.Thread(target=self.errorMonitor,args=(),name='ERROR')
        errorThread.daemon = True
        errorThread.start()

        #Start threads
        self.startVicon()
        time.sleep(2)
        self.startControl()


        # if self.logEnabled ==True:
        #     self.startLog()


        if self.printUpdateRate:
            t = threading.Thread(target=self.printQ,args=())
            t.daemon = True
            t.start()





    def errorMonitor(self):
        while self.active:
            ERROR = self.QueueList["error"].get()
            if ERROR:
                print(ERROR)
                print('sent kill')
                self.QueueList["kill"].put(True)
                time.sleep(0.1)
                return


    def startVicon(self):
        print("Connecting to vicon stream. . .")
        self.cf_vicon = viconStream(self.name,self.QueueList)
        # self.cf_vicon = viconStream(self.name,self.vicon_queue,self.error_queue)



    def startControl(self):
        self.t1 = time.time()
        print("Starting control thread. . .")
        # self.ctrl = PID_CLASS(self.vicon_queue,self.setpoint_queue,self.logger_queue,self.kill_queue)
        self.ctrl = PID_CLASS(self.QueueList)




    def startPlots(self):
        self.plots = responsePlots()


    def startLog(self):
        self.logger = logger(self.logger_queue,self.logName)



    def printQ(self):
        while self.active:
            print('Vicon update rate:',self.cf_vicon.update_rate,'\t','PID update rate:',self.ctrl.update_rate)#,'\t','Log:',self.logger.update_rate,'\t')
            time.sleep(0.5)
            # os.system('cls')
            # print('Vicon Q:',self.vicon_queue.qsize(),'\t','SP Q:',self.setpoint_queue.qsize(),'\t','Logger Q:',self.logger_queue.qsize(),'time',str(time.time()-self.t1))






    def takeoff(self,height):
        sp = {}
        X = self.QueueList["vicon"].get()
        sp["x"] = X["x"]
        sp["y"] = X["y"]
        sp["z"] = height
        self.QueueList["sp"].put(sp)

    def land(self):
        sp = {}
        X = self.QueueList["vicon"].get()
        sp["x"] = X["x"]
        sp["y"] = X["y"]
        sp["z"] = X["z"]
        while sp["z"]>0:
            sp["z"] = sp["z"]-0.01
            self.QueueList["sp"].put(sp)
            time.sleep(0.04)

        self.QueueList["kill"].put(True)


    def goto(self,x,y,z):
        sp = {}
        sp["x"] = x
        sp["y"] = y
        sp["z"] = z
        self.QueueList["sp"].put(sp)


