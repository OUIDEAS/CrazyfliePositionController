import numpy as np
from matplotlib import pyplot as plt
from guidance.dubinsUAV import dubinsUAV



class vectorField():
    def __init__(self):


        self.curr_cmd = []


        #Summed Guidance Parameters
        self.normSummedFields = True
        self.avfWeight = 1
        self.rvfWeight = 1


        #Path Parameters
        self.pathAngle = np.pi/2
        self.normPathConvergence = False
        self.normPathCirculation = False
        self.normPathTotal = True
        self.pathG = -1
        self.pathH = 10

        #Obstacle Paramemters
        self.normObstConvergence = True
        self.normObstCirculation = True
        self.normObstTotal = True
        self.obstDecayActive = True

        self.xc = 0
        self.yc = 0
        self.r = 0.01
        self.decayR = 30
        self.obstG = 1
        self.obstH = 10
        self.gamma = 1

        #Plotting Functionality

        self.x_range = np.linspace(-2, 2, 25)
        self.y_range = self.x_range
        self.x_start = -2

        self.Us = np.empty((len(self.x_range), len(self.x_range)))
        self.Us[:] = np.nan

        self.Vs = np.empty((len(self.x_range), len(self.x_range)))
        self.Vs[:] = np.nan

        self.Xs, self.Ys = np.meshgrid(self.x_range, self.y_range)


        self.velocity = 0.25
        self.dubinsUAV = dubinsUAV()
        self.dubinsUAV.setup(self.x_start, 0, self.velocity, 0, 0.1)



        pass


    def setupObst(self,obstY,obstX,gamma):

        self.obstR = self.dubinsUAV.v / 0.35
        self.obstY = obstY
        self.obstX = obstX
        self.xc = obstX
        self.yc = obstY

        self.decayR = self.dubinsUAV.turn_radius*gamma+self.obstR
        self.pathH = 2*self.dubinsUAV.v


    def calcPath(self,x,y):
        a = 2*x*np.square(np.cos(self.pathAngle))+2*np.cos(self.pathAngle)*np.sin(self.pathAngle)*y
        b = 2*y*np.square(np.sin(self.pathAngle))+2*np.cos(self.pathAngle)*np.sin(self.pathAngle)*x
        c = 2
        path_convergence = np.array([[a],[b]])

        if self.normPathConvergence:
            mag = np.sqrt(np.square(path_convergence[0])+np.square(path_convergence[1]))
            path_convergence = np.divide(path_convergence,mag)


        a = np.sin(self.pathAngle)
        b = -np.cos(self.pathAngle)
        path_circulation = np.array([[a],[b]])

        if self.normPathCirculation:
            mag = np.sqrt(np.square(path_circulation[0])+np.square(path_circulation[1]))
            path_circulation = np.divide(path_circulation,mag)

        gv = self.pathG*path_convergence+self.pathH*path_circulation

        if self.normPathTotal:
            mag = mag = np.sqrt(np.square(gv[0])+np.square(gv[1]))
            gv = np.divide(gv,mag)
        return gv


    def calcObst(self,x,y):
        x_bar = x - self.xc
        y_bar = y - self.yc


        a = 2*x_bar**3  +   2*x_bar*y_bar**2    -   2*self.r**2*x_bar
        b = 2*y_bar**3  +   2*x_bar**2*y_bar    -   2*self.r**2*y_bar
        obst_convergence = np.array([[a],[b]])


        obst_circulation = np.array([[2*(y_bar)],[-2*x_bar]])

        try:
            if self.normObstConvergence:
                mag = np.sqrt(np.square(obst_convergence[0])+np.square(obst_convergence[1]))
                obst_convergence = np.divide(obst_convergence,mag)
        except:
            pass

        try:
            if self.normObstCirculation:
                mag = np.sqrt(np.square(obst_circulation[0])+np.square(obst_circulation[1]))
                obst_circulation = np.divide(obst_circulation,mag)
        except:
            pass


        gv = self.obstG*obst_convergence+self.obstH*obst_circulation

        if self.normObstTotal:
            mag  = np.sqrt(np.square(gv[0])+np.square(gv[1]))
            gv = np.divide(gv,mag)


        if self.obstDecayActive:
            range = np.sqrt((x_bar)**2+(y_bar)**2)
            p = -(np.tanh(2 * np.pi * range / self.decayR - np.pi)) + 1
            gv = p*gv




        return gv


    def getVFatXY(self,x,y):

        path = self.calcPath(x,y)
        obst = self.calcObst(x,y)

        gv = self.avfWeight*path+self.rvfWeight*obst

        if self.normSummedFields:
            mag = np.sqrt(np.square(gv[0]) + np.square(gv[1]))
            gv = np.divide(gv,mag)

        return gv


    def getOptVF(self,uav):
        if uav.x <= (uav.turn_radius * self.gamma + self.obstR):

            alpha = np.arctan2(uav.y - self.obstY, uav.x)
            beta = np.pi - alpha + uav.heading
            range = np.sqrt((uav.x - self.obstX)**2 + (uav.y - self.obstY)**2)


            turnR = uav.turn_radius

            y = turnR * (1 - np.cos(np.pi / 2))
            X = self.obstX - np.sqrt((turnR + self.obstR)**2 - (y - self.obstY)**2)
            theta = np.arcsin((y - self.obstY) / (self.obstR + turnR))
            zeta = np.pi + theta
            X_turn = (-X + turnR * np.cos(zeta))
            Y_turn = y + turnR * np.sin(zeta)


            if abs(uav.x) <= abs(X * 1.02) and alpha > np.arctan2(Y_turn, X_turn):
                self.rvfWeight = 1
                self.avfWeight = 1 / 8

                g = - uav.v * np.cos(abs(beta)) - abs(1 / ((range - self.obstR) * uav.v))
                g = -(uav.v+abs(1/((range-self.obstR))))*np.cos(abs(beta))
                if g > 0:
                    g = 0

                self.obstG = -g

                if uav.y <= Y_turn and uav.x >= X_turn:
                    self.avfWeight = 1
                    self.rvfWeight = 0
            else:
                self.avfWeight = 1
                self.rvfWeight = 0

        path = self.calcPath(uav.x, uav.y)
        obst = self.calcObst(uav.x, uav.y)

        gv = self.avfWeight * path + self.rvfWeight * obst

        if self.normSummedFields:
            mag = np.sqrt(np.square(gv[0]) + np.square(gv[1]))
            gv = np.divide(gv, mag)

        return gv

    def getOptVF2(self, uav_x,uav_y,uav_tr,uav_heading,uav_v):


        if uav_x <= (self.obstR* self.gamma + self.obstR):
            alpha = np.arctan2(uav_y - self.obstY, uav_x)
            beta = np.pi - alpha + uav_heading
            range = np.sqrt((uav_x - self.obstX) ** 2 + (uav_y - self.obstY) ** 2)

            turnR = uav_tr

            y = turnR * (1 - np.cos(np.pi / 2))
            X = self.obstX - np.sqrt((turnR + self.obstR) ** 2 - (y - self.obstY) ** 2)
            theta = np.arcsin((y - self.obstY) / (self.obstR + turnR))
            zeta = np.pi + theta
            X_turn = (-X + turnR * np.cos(zeta))
            Y_turn = y + turnR * np.sin(zeta)


            if uav_x < abs(X) * 1.02 and alpha > np.arctan2(Y_turn, X_turn):
                self.rvfWeight = 1
                self.avfWeight = 1 / 8

                g = - uav_v * np.cos(abs(beta)) - abs(1 / ((range - self.obstR) * uav_v))
                g = -(uav_v + abs(1 / ((range - self.obstR)))) * np.cos(abs(beta))
                if g > 0:
                    g = 0
                self.obstG = -g

                if abs(uav_y) < abs(Y_turn) and uav_x > X_turn:
                    self.avfWeight = 1
                    self.rvfWeight = 0
            else:
                self.avfWeight = 1
                self.rvfWeight = 0

        else:
            self.avfWeight = 1
            self.rvfWeight = 0

        path = self.calcPath(uav_x, uav_y)
        obst = self.calcObst(uav_x, uav_y)

        gv = self.avfWeight * path + self.rvfWeight * obst

        if self.normSummedFields:
            mag = np.sqrt(np.square(gv[0]) + np.square(gv[1]))
            gv = np.divide(gv, mag)

        return gv

    def pltObstacle(self):

        theta = np.linspace(0,2*np.pi,100)
        cxs = self.xc+self.obstR*np.cos(theta)
        cys = self.yc+self.obstR*np.sin(theta)
        plt.plot(cxs,cys,'b')

    def calcFullField(self):
        for i in range(0, len(self.x_range)):
            for j in range(0, len(self.y_range)):
                Vg = self.getVFatXY(self.x_range[i], self.y_range[j])
                self.Us[i][j] = Vg[0][0]
                self.Vs[i][j] = Vg[1][0]
                self.Xs[i][j] = self.x_range[i]
                self.Ys[i][j] = self.y_range[j]




    def plotPosition(self,x,y,heading,vx,vy,v,turn_radius,carrot_d):
        plt.cla()


        #Get vector and update field parameters
        #Calculate full field

        #Plot full field
        #Plot obstacle
        #Plot UAV position
        #Plot UAV velocity vector
        #Plot CMDED UAV vector
        #Plot Carrot position

        Vg = self.getOptVF2(x, y, turn_radius, heading, v)
        cmd_heading = np.arctan2(Vg[1], Vg[0])
        self.calcFullField()


        plt.quiver(self.Xs, self.Ys, self.Us, self.Vs)



        x_cmd = carrot_d * np.cos(heading)+x
        y_cmd = carrot_d * np.sin(heading)+y
        plt.plot(x_cmd,y_cmd,'r*')

        THETA = np.linspace(0,2*np.pi,100)
        plt.plot(self.decayR*np.cos(THETA),self.decayR*np.sin(THETA))

        plt.quiver(x, y, vx, vy, color='b')
        plt.quiver(x, y, Vg[0], Vg[1], color='r')
        plt.axis('equal')
        plt.axis([-5,5,-5,5])

        self.curr_cmd = heading



    def simulateDubins(self):
        velocity = 0.25

        self.dubinsUAV.setup(self.x_start, 0, velocity, 0, 0.1)
        plt.ion()
        while self.dubinsUAV.x < -1 * self.x_start:
            plt.cla()
            self.calcFullField()
            plt.quiver(self.Xs, self.Ys, self.Us, self.Vs)

            # Vg = self.getOptVF(self.dubinsUAV)

            uav_x = self.dubinsUAV.x
            uav_y = self.dubinsUAV.y
            uav_tr = self.dubinsUAV.turn_radius
            uav_heading = self.dubinsUAV.heading
            uav_v = self.dubinsUAV.v

            Vg = self.getOptVF2(uav_x,uav_y,uav_tr,uav_heading,uav_v)
            heading = np.arctan2(Vg[1], Vg[0])
            self.dubinsUAV.update_pos(heading)
            self.pltObstacle()
            plt.plot(self.dubinsUAV.xs, self.dubinsUAV.ys, 'r')
            plt.quiver(self.dubinsUAV.x, self.dubinsUAV.y, self.dubinsUAV.vx, self.dubinsUAV.vy, color='b')
            plt.quiver(self.dubinsUAV.x, self.dubinsUAV.y, Vg[0], Vg[1], color='r')

            plt.axis('equal')

            plt.pause(0.01)























