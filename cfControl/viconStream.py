import threading
import time
import viconClient


class viconStream():
    def __init__(self, name,q):
        self.name = name
        self.X = {}
        self.X["x"] = []
        self.X["y"] = []
        self.X["z"] = []
        self.X["yaw"] = []
        self.X["yawRate"] = []


        self.sleep_rate = 0.01
        self.update_rate = []

        thread = threading.Thread(target=self.run, args=(q,))
        self.lock = threading.Lock()
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self,q):
        vc = viconClient.viconClient("192.168.0.197",801)
        vc.vicon_connect()
        print("Connected to vicon stream")
        time.sleep(1)
        print("starting to send position command!")

        X = vc.getPos(self.name)
        yaw_previous = X["yaw"]


        while True:
            t1 = time.time()
            yaw_previous = X["yaw"]
            X = vc.getPos(self.name)
            self.X["x"] = X["x"]
            self.X["y"] = X["y"]
            self.X["z"] = X["z"]
            self.X["yaw"] = X["yaw"]
            self.X["yawRate"] = (X["yaw"]-yaw_previous) / self.sleep_rate

            if q.full():
                print('Warning, vicon queue is full')
            else:
                q.put(self.X)


            time.sleep(self.sleep_rate)
            t2 = time.time()

            self.update_rate = 1/(t2-t1)
            # print(self.update_rate)








