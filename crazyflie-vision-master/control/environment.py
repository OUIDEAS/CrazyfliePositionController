import numpy as np
import math
# import matplotlib as plt

class hullData:
    def __init__(self):
        self.name = 0
        self.path = []
        self.xlim = []
        self.ylim = []
        self.x_in = []
        self.y_in = []
        self.nu = []
        self.nv = []
        self.VF = []
        self.line_theta = []
        self.geofence = []



class enviro:
    def __init__(self):
        self.hullList = []

    def checkPoints(self, x, y, check=True):
        for i in range(0,len(self.hullList)):
            self.hullList[i].geofence = []
            for j in range(0,len(self.hullList[i].xlim)):
                self.hullList[i].geofence.append((self.hullList[i].xlim[j],self.hullList[i].ylim[j]))
            for k in range(0,len(x)):
                for l in range(0,len(x)):
                    inzone = point_in_poly(x[k][l],y[k][l],self.hullList[i].geofence)
                    if inzone == True:
                        self.hullList[i].x_in.append(x[k][l])
                        self.hullList[i].y_in.append(y[k][l])

    def calcVF(self):
        for i in range(0,len(self.hullList)):
            self.hullList[i].line_theta = math.atan2(self.hullList[i].path[1][1] - self.hullList[i].path[1][0],
                                                     self.hullList[i].path[0][1] - self.hullList[i].path[0][0]) + np.pi/2
            for j in range(0,len(self.hullList[i].x_in)):
                V = []
                G = 3

                xc = self.hullList[i].path[0][1]
                yc = self.hullList[i].path[1][1]

                a = 1 * np.cos(self.hullList[i].line_theta)
                b = 1 * np.sin(self.hullList[i].line_theta)
                a1 = a * (self.hullList[i].x_in[j] - xc) + b * (self.hullList[i].y_in[j] - yc)
                ga1 = np.array([a, b, 0])
                a2 = 0
                ga2 = np.array([0,0, 1])
                Vcnv = -G * (a1 * ga1 + a2 * ga2)
                Vcrc = np.cross(ga1, ga2)
                TV = [0, 0, 0]


                # Vcnv = Vcnv / np.linalg.norm(Vcnv)
                # Vcrc = Vcrc / np.linalg.norm(Vcrc)

                conv = Vcnv
                circ = Vcrc
                tv = TV
                V = conv + circ + tv


                self.hullList[i].nu.append(V[0])
                self.hullList[i].nv.append(V[1])

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