
import time
import socket
import json
import posq





class groundRobot():
    def __init__(self,name,QueueList):

        self.name = name
        self.QueueList = QueueList
        self.active = True


        #setup UDP

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = "192.168.0.192"
        self.port = 5555

        pass




    def run(self):


        while self.active:

            X = self.QueueList["sp"].get()


            xnow = [X["x"],X["Y"],heading]
            output = posq.step(t, xnow, XCMD, direction, old_beta, vmax, base)




            message = json.dumps(cmd)
            self.client_socket.sendto(message, (self.addr, self.port))


            pass