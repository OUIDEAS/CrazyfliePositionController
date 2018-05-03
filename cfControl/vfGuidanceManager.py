import threading
import numpy as np
import time
from guidance.vectorField import vectorField
from matplotlib import pyplot as plt

class vfGuidance():

    def __init__(self,name,QueueList,carrot,alt=0.25):

        self.name = name
        self.carrot_d = carrot
        self.QueueList = QueueList
        self.alt = alt
        self.sleep_rate = 1
        self.message = {}
        self.active = True
        self.sp = {}
        self.sp["x"] = []
        self.sp["y"] = []
        self.sp["z"] = []
        t = threading.Thread(target=self.run,args=())
        t.daemon = True
        t.start()


    def run(self):

        self.message["mess"] = 'VF_GUIDANCE_MANAGER_START'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)

        gamma = 1.0
        vf = vectorField()


        vf.setupObst(0, 0, gamma)
        vf.obstH = 6.1

        turn_rate = 0.35
        vf.rvfWeight = 0
        x_new = []
        y_new = []
        x_old = []
        y_old = []
        heading = []

        vx = []
        vy = []
        v =  []

        X = self.QueueList["vicon_utility"].get()
        x_new = X["x"]
        y_new = X["y"]
        time.sleep(self.sleep_rate)

        plt.ion()
        while self.active:
            try:
                #Calculate States
                x_old = x_new
                y_old = y_new
                X = self.QueueList["vicon_utility"].get()
                x_new = X["x"]
                y_new= X["y"]
                vx = (x_new-x_old)/self.sleep_rate
                vy = (y_new-y_old)/self.sleep_rate
                v = np.sqrt(vx**2+vy**2)
                print(v)
                heading = np.arctan2(vy,vx)
                turn_radius = v / turn_rate



                Vg = vf.getOptVF2(x_new, y_new, turn_radius, heading, v)
                cmd_heading = np.arctan2(Vg[1], Vg[0])
                # vf.calcFullField()
                x_cmd = self.carrot_d * np.cos(cmd_heading) + x_new
                y_cmd = self.carrot_d * np.sin(cmd_heading) + y_new


                # self.plotSystemState(vf,x_new,y_new,vx,vy,Vg[0],Vg[1],x_cmd,y_cmd)


                #Send to PID
                self.sp["x"] = float(x_cmd)
                self.sp["y"] = float(y_cmd)
                self.sp["z"] = float(self.alt)

                self.QueueList["sp"].put(self.sp,block=False)
                time.sleep(self.sleep_rate)


                # print("AVFW:",vf.avfWeight,"\t","RVFW:",vf.rvfWeight)
            except:
                pass



        self.message["mess"] = 'VF_GUIDANCE_COMPLETE'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)



    def plotSystemState(self,vf,x,y,vx,vy,u_cmd,v_cmd,x_cmd,y_cmd):

        plt.cla()
        # Plot UAV position
        # Plot UAV velocity vector
        # Plot CMDED UAV vector
        # Plot Carrot position
        THETA = np.linspace(0, 2 * np.pi, 100)

        # plt.quiver(vf.Xs, vf.Ys, vf.Us, vf.Vs)
        plt.plot(vf.obstR*np.cos(THETA),vf.obstR*np.sin(THETA))
        # plt.quiver(x, y, vx, vy, color='b')
        plt.quiver(x, y, u_cmd, v_cmd, color='r')
        plt.plot(x_cmd,y_cmd,'r*')
        plt.axis('equal')
        plt.axis([-5,5,-5,5])
        plt.pause(self.sleep_rate)


