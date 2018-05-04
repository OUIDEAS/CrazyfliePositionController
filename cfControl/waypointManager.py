import threading
import numpy as np
import time

class waypointManager():

    def __init__(self,name,QueueList):

        self.name = name
        # self.WPradius = WPradius
        self.QueueList = QueueList
        self.currentWP = 0
        self.sleep_rate = 0.1
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

        self.message["mess"] = 'WAYPOINT_MANAGER_START'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)

        WPradius = .20

        L = 2 * WPradius + 10

########################################################################################################################
        # opens the text file containing the waypoints and puts them into the list 'waypoint'
        with open("wpts.txt") as file:
            waypoint = []
            for line in file:
                waypoint.append(line.rstrip().split(","))

        WPx = []
        WPy = []

        for x in range(0, len(waypoint)):
            WPx.append(int(waypoint[x][0]))
            WPy.append(int(waypoint[x][1]))

        # WPx = []
        # WPy = []
        #
        # WPx.append(0.5)
        # WPy.append(0.5)
        #
        # WPx.append(-0.5)
        # WPy.append(0.5)
        #
        # WPx.append(-1/2)
        # WPy.append(-1/2)
        #
        # WPx.append(1/2)
        # WPy.append(-1/2)
        #
        # WPx.append(0)
        # WPy.append(0)
########################################################################################################################
        wptx = WPx[self.currentWP]
        wpty = WPy[self.currentWP]

        self.sp["x"] = wptx
        self.sp["y"] = wpty
        self.sp["z"] = 0.5
        self.QueueList["sp"].put(self.sp)

        while self.active:
            time.sleep(self.sleep_rate)
            wptx = WPx[self.currentWP]
            wpty = WPy[self.currentWP]
            X = self.QueueList["vicon_utility"].get()
            x = X["x"]
            y = X["y"]

            try:
                dx = wptx - x                   # change in x between the Waypoint and the UAV
                dy = wpty - y                   # change in y between the Waypoint and the UAV

                alpha = np.arctan2(dy, dx)      # angle between UAV and the current Waypoint measured from the x-axis

                A = x + L * np.cos(alpha)       # current x-position of the Dummy Point
                B = y + L * np.sin(alpha)       # current y-position of the Dummy point

                dA = wptx - A                   # change in x between the Waypoint and the Dummy Point
                dB = wpty - B                   # change in y between the Waypoint and the Dummy Point

                DUMMYtoWPT = np.sqrt(dA * dA + dB * dB) # calculate the distance between the Dummy Point and the Waypoint
                UAVtoWPT = np.sqrt(dx * dx + dy * dy)   # calculate the distance between the UAV and the Waypoint

                if DUMMYtoWPT >= UAVtoWPT:          # if the distance from the Dummy Point to the waypoint is greater than
                                                    # the distance from the UAV to the Waypoint...
                    if UAVtoWPT <= WPradius:   # ...and the distance from the UAV to the Waypoint is less than the specified radius
                        if not self.currentWP == len(WPx)-1:
                            self.message["mess"] = 'WAYPOINT_REACHED'
                            self.message["data"] = self.name
                            self.QueueList["threadMessage"].put(self.message)
                            self.currentWP = self.currentWP + 1  # change to the next Waypoint
                            wptx = WPx[self.currentWP]
                            wpty = WPy[self.currentWP]
                            self.sp["x"] = wptx
                            self.sp["y"] = wpty
                            self.sp["z"] = 0.5
                            self.QueueList["sp"].put(self.sp,block=False)
                        else:
                            self.active = False
                            self.message["mess"] = 'LAST_WAYPOINT_REACHED'
                            self.message["data"] = self.name
                            self.QueueList["threadMessage"].put(self.message)

            except:
                print("waypointManager exception met")

        self.message["mess"] = 'WAYPOINT_FOLLOWING_COMPLETE'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)

        print("WAYPOINT FOLLOWING COMPLETE")