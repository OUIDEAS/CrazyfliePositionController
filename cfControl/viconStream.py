import threading
import time
import viconClient


class viconStream():
    # def __init__(self, name,q,error_queue):
    def __init__(self, name,QueueList):
        self.name = name
        self.X = {}
        self.X["x"] = []
        self.X["y"] = []
        self.X["z"] = []
        self.X["yaw"] = []
        self.X["yawRate"] = []
        self.MaxDeadPackets = 20


        self.sleep_rate = 0.01
        self.update_rate = []

        thread = threading.Thread(target=self.run, args=(QueueList,))
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self,QueueList):
        vc = viconClient.viconClient("192.168.0.197",801)
        vc.vicon_connect()
        print("Connected to vicon stream for ",self.name)
        time.sleep(1)
        print("Attempting to rec data for ",self.name)

        try:
            X = vc.getPos(self.name)
            self.yp = X["yaw"]

        except KeyError:
            error = 'No initial data rec from ' + self.name
            QueueList["error"].put(error)
            return


        DeadPacketCount = 0
        while True:
            t1 = time.time()
            X = vc.getPos(self.name)
            if X["x"] is not False:
                self.X["x"] = X["x"]
                self.X["y"] = X["y"]
                self.X["z"] = X["z"]
                self.X["yaw"] = X["yaw"]
                self.X["yawRate"] = (X["yaw"]-self.yp) / self.sleep_rate
                self.yp = X["yaw"]
                DeadPacketCount = 0

                if QueueList["vicon"].full():
                    pass
                    # print('Warning, vicon queue is full')
                else:
                    QueueList["vicon"].put(self.X)

                time.sleep(self.sleep_rate)
                t2 = time.time()
                self.update_rate = 1 / (t2 - t1)

            else:
                if DeadPacketCount >= self.MaxDeadPackets:
                    error = 'Number of dead packets exceeded for ' + self.name
                    QueueList["error"].put(error)
                    return
                DeadPacketCount=DeadPacketCount+1











