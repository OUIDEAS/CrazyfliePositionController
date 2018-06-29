
import numpy as np

class dubinsUAV():

    def __init__(self):


        self.useDubins = True
        self.v = 0.25
        self.dt = 0.1
        self.t = 0
        self.turnrate = 0.35
        self.turn_radius = []

        #Current state
        self.x = []
        self.y = []
        self.vx = []
        self.vy = []
        self.heading = []
        self.cmdHeading = []
        self.flightEnvX = []
        self.flightEnvY = []

        # History
        self.xs = np.array([])
        self.ys = np.array([])
        self.vxs = np.array([])
        self.vys = np.array([])
        self.headings = np.array([])
        self.headingcmds = np.array([])
        self.ts = np.array([])



    def setup(self,x0,y0,v,heading0,dt):
        self.x = x0
        self.y = y0
        self.v = v
        self.heading = heading0
        self.vx = v * np.cos(heading0)
        self.vy = v * np.sin(heading0)
        self.dt = dt

        self.xs = x0
        self.ys = y0
        self.headings = heading0
        self.headingcmds = heading0
        self.ts = 0

        self.turn_radius = self.v / self.turnrate


    def update_pos(self,heading):

        VF_heading = heading

        if self.useDubins:

            theta = np.arctan2(self.vy, self.vx)
            if abs(theta - VF_heading) < np.pi:
                if theta - VF_heading < 0:
                    theta = theta + self.turnrate * self.dt
                else:
                    theta = theta - self.turnrate * self.dt

            else:
                if theta - VF_heading > 0:
                    theta = theta + self.turnrate * self.dt
                else:
                    theta = theta - self.turnrate * self.dt

        else:
            theta = VF_heading


        # Update States
        self.t = self.t + self.dt
        self.heading = theta
        self.cmdHeading = VF_heading

        self.vx = self.v * np.cos(theta)
        self.vy = self.v * np.sin(theta)
        self.x = self.x + self.vx * self.dt
        self.y = self.y + self.vy * self.dt

        #Update flight nvelope
        # self.calcFlightEnv()

        # Update History

        self.xs = np.append(self.xs,self.x)
        self.ys = np.append(self.ys,self.y)
        self.vxs = np.append(self.vxs, self.vx)
        self.vys = np.append(self.vys, self.vy)
        self.headings = np.append(self.headings,self.heading)
        self.ts = np.append(self.ts,self.t)


