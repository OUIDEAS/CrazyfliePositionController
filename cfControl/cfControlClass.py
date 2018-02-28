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
        self.printUpdateRate = True
        self.active = True
        #Class Settings
        self.name = uavName
        self.logEnabled = logEnabled[0]
        self.logName = logEnabled[1]

        #Queue Dictionary
        self.QueueList = {}
        self.QueueList["vicon"] = Queue()
        self.QueueList["sp"] = Queue()
        self.QueueList["log"] = Queue()


        #Currently used poorly. Updated error queue will be shared with all threads and read by a system monitor.
        #Errors will be read and recorded
        #Errors that call for a throttle down or shutdown will send commands to control thread over controlShutDown queue

        self.QueueList["threadMessage"] = Queue()
        #Thread message is a dictionary
        #message = {}
        #message["message"] = string
        #message["data"] = other message data
        #Queue intended to be read by the control class only for two purposes
        # 1) Throttle down - intended for slow geofence breaches
        # 2) Kill - Sends 0 on all control variables to shut down motors
        self.QueueList["controlShutdown"] = Queue()



        # Startup Proceedure
        # 1) Message Monitor
        # 2) Vicon
        # 3) PID

        thread = threading.Thread(target=self.messageMonitor, args=())
        thread.daemon = True
        thread.start()



        self.startVicon()
        time.sleep(3)
        self.startControl()

        updown = threading.Thread(target=self.upDown,args=())
        updown.daemon = True
        updown.start()


        if self.printUpdateRate:
            t = threading.Thread(target=self.printQ,args=())
            t.daemon = True
            t.start()


    def messageMonitor(self):
        print('Starting message monitor')
        time.sleep(1)
        while True:
                try:
                    message = self.QueueList["threadMessage"].get(block=False)
                    if message["mess"] == "VICON_CONNECTED":
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))

                    elif message["mess"] == 'NO_INIT_VICON_DATA':
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))

                    elif message["mess"] == 'VICON_DATA_FULL':
                        print(message["mess"], '\t', "Queue size:", str(message["data"]))

                    elif message["mess"] == 'DEAD_PACKET_EXCEEDS_LIMIT':
                        print(message["mess"], '\t', str(message["data"]))
                        self.cf_vicon.active=False

                    elif message["mess"] == 'VICON_DEACTIVATED':
                        print(message["mess"], '\t', str(message["data"]))



                    #Control messages
                    elif message["mess"] == 'MOTOR_UNLOCK_SENT':
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))

                    elif message["mess"] == 'VICON_QUEUE_EXCEPTION_ERROR':
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))


                    elif message["mess"] == 'NEW_SP_ACCEPTED':
                        print(message["mess"], '\t', "Position:", str(message["data"]))



                    elif message["mess"] == 'ATTEMPTING_TO_SEND_KILL_CMD':
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))

                    elif message["mess"] == 'KILL_CMD_SENT':
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))


                    elif message["mess"] == 'THROTTLE_DOWN_START':
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))

                    elif message["mess"] == 'THROTTLE_DOWN_COMPLETE':
                        print(message["mess"], '\t', "Object Name:", str(message["data"]))

                    else:
                        print(message)
                except:
                    pass
                time.sleep(0.01)



    def startVicon(self):
        print("Connecting to vicon stream. . .")
        self.cf_vicon = viconStream(self.name,self.QueueList)
        # self.cf_vicon = viconStream(self.name,self.vicon_queue,self.error_queue)

    def startControl(self):
        self.t1 = time.time()
        print("Starting control thread. . .")
        # self.ctrl = PID_CLASS(self.vicon_queue,self.setpoint_queue,self.logger_queue,self.kill_queue)
        self.ctrl = PID_CLASS(self.QueueList,self.name)

    def startLog(self):
        self.logger = logger(self.logger_queue,self.logName)



#######################################################################################################################
    # Debugging utilities

    def printQ(self):
        while self.active:
            # print('Vicon update rate:',self.cf_vicon.update_rate,'\t','PID update rate:',self.ctrl.update_rate)#,'\t','Log:',self.logger.update_rate,'\t')
            print('Vicon update rate:',self.cf_vicon.update_rate,'\t','PID:',self.ctrl.update_rate,'\t')

            time.sleep(0.5)
            # os.system('cls')




    def upDown(self):
        while True:
            time.sleep(5)
            self.takeoff(1)
            time.sleep(2)
            self.QueueList["controlShutdown"].put('THROTTLE_DOWN')
            time.sleep(5)
            self.land()



#######################################################################################################################
        #User end functions


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
            time.sleep(0.1)

        # self.QueueList["kill"].put(True)


    def goto(self,x,y,z):
        sp = {}
        sp["x"] = x
        sp["y"] = y
        sp["z"] = z
        self.QueueList["sp"].put(sp)


