import numpy as np
import math

class UAV:
    turnRate = 0
    turnRad = 0
    x = 0
    y = 0
    x_look = 0
    y_look = 0
    u = 0
    v = 0
    vel = 0
    vic_heading = 0
    theta = 0
    vx = 0
    vy = 0
    j = 0
    inside_hulls = True
    isSim = True
    lookAhead = False
    lookAheadADD = False
    modPred = False
    dt = .1
    number = 0
    xstore = []
    ystore = []
    ustore = []
    vstore = []


    def __init__(self,env):
        self.x = 0
        self.y = 0
        self.vel = 2
        self.theta = 0
        self.dt = .1
        self.vx = 1
        self.vy = 0
        self.turnRate = 1.5
        self.turnRad = 1
        self.findHulls(env)

    def findHulls(self,env):
        for q in range(0,len(env.hullList)):
            if self.lookAhead:
                inzone = point_in_poly(self.x_look, self.y_look, env.hullList[q].geofence)
            else:
                inzone = point_in_poly(self.x, self.y, env.hullList[q].geofence)

            self.j = q
            if inzone == True:
                self.inside_hulls = True
                break

            if self.j == len(env.hullList) - 1:
                if inzone == False:
                    self.inside_hulls = False


    def calcTurns(self):
        self.turnRad = self.vel/self.turnRate

        turnRadLxc = self.x + self.turnRad*np.cos(self.theta + np.pi/2)
        turnRadLyc = self.y + self.turnRad*np.sin(self.theta + np.pi/2)

        turnRadRxc = self.x + self.turnRad*np.cos(self.theta + 3*np.pi/2)
        turnRadRyc = self.y + self.turnRad*np.sin(self.theta + 3*np.pi/2)

        thetaL = np.linspace(self.theta,self.theta-(np.pi/2),10)
        thetaR = np.linspace(self.theta, self.theta + (np.pi / 2), 10)
        self.turnRadL = []
        self.turnRadLx = turnRadLxc+self.turnRad*np.cos(thetaL)
        self.turnRadLy = turnRadLyc+self.turnRad*np.sin(thetaL)
        self.turnRadRx = turnRadRxc + self.turnRad*np.cos(thetaR)
        self.turnRadRy = turnRadRyc + self.turnRad*np.sin(thetaR)


    def getVF(self,env):
        V = []
        G = 3
        xc = env.hullList[self.j].path[0][1]
        yc = env.hullList[self.j].path[1][1]
        a = np.cos(env.hullList[self.j].line_theta)
        b = np.sin(env.hullList[self.j].line_theta)

        if self.isSim:
            self.vic_heading = self.theta

        numPointsCirc = 18
        phi = np.linspace(0,2*np.pi,numPointsCirc)

        self.x_look = self.x + 2*np.cos(self.vic_heading)  # 2,sim .25,robo
        self.y_look = self.y + 2*np.sin(self.vic_heading)
        x_calc = self.x
        y_calc = self.y

        xadd = 0
        yadd = 0
        count = 0
        vadd = [0,0,0]
        vavg = [0, 0, 0]
        self.modArray = []

        if self.lookAhead:
            x_calc = self.x_look
            y_calc = self.y_look

            if self.lookAheadADD:
                x_calc = self.x
                y_calc = self.y

                xadd = self.x
                yadd = self.y
                a1 = a * (xadd - xc) + b * (yadd - yc)
                ga1 = np.array([a, b, 0])
                a2 = 0
                ga2 = np.array([0, 0, 1])
                Vcnv = -G * (a1 * ga1 + a2 * ga2)
                Vcrc = np.cross(ga1, ga2)
                TV = [0, 0, 0]
                conv = Vcnv
                circ = Vcrc
                tv = TV
                vadd = (conv + circ + tv)


        a1 = a * (x_calc - xc) + b * (y_calc - yc)
        ga1 = np.array([a, b, 0])
        a2 = 0
        ga2 = np.array([0, 0, 1])
        Vcnv = -G * (a1 * ga1 + a2 * ga2)
        Vcrc = np.cross(ga1, ga2)
        TV = [0, 0, 0]
        conv = Vcnv
        circ = Vcrc
        tv = TV
        V = conv + circ + tv

        self.xstore.append(self.x)
        self.ystore.append(self.y)
        self.ustore.append(V[0])
        self.vstore.append(V[1])


        self.u = vadd[0]+V[0]
        self.v = vadd[1]+V[1]



    def getheading(self):
        if self.isSim:
            self.useDubins = True
        else:
            self.useDubins = False

        if self.useDubins:
            phi = math.atan2(self.vy, self.vx)
            beta = math.atan2(self.v, self.u)
            if abs(phi - beta) < np.pi:
                if phi - beta < 0:
                    phi = phi + self.turnRate * self.dt
                else:
                    phi = phi - self.turnRate * self.dt

            else:
                if phi - beta > 0:
                    phi = phi + self.turnRate * self.dt
                else:
                    phi = phi - self.turnRate * self.dt

            self.theta = phi



        else:
            self.theta = math.atan2(self.v, self.u)

        self.calcTurns()

    def updatePos(self):
        self.vx = self.vel * np.cos(self.theta)
        self.vy = self.vel * np.sin(self.theta)

        self.x = self.x + self.vx * self.dt
        self.y = self.y + self.vy * self.dt

    def runUAV(self,env):
        self.findHulls(env)
        self.getVF(env)
        self.getheading()

        if self.isSim:
            self.updatePos()



def point_in_poly(x, y, poly, include_edges=True):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if p1y == p2y:
            if y == p1y:
                if min(p1x, p2x) <= x <= max(p1x, p2x):
                    # point is on horisontal edge
                    inside = include_edges
                    break
                elif x < min(p1x, p2x):  # point is to the left from current edge
                    inside = not inside
        else:  # p1y!= p2y
            if min(p1y, p2y) <= y <= max(p1y, p2y):
                xinters = (y - p1y) * (p2x - p1x) / float(p2y - p1y) + p1x

                if x == xinters:  # point is right on the edge
                    inside = include_edges
                    break

                if x < xinters:  # point is to the left from current edge
                    inside = not inside

        p1x, p1y = p2x, p2y

    return inside