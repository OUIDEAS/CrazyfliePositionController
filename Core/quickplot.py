
import matplotlib.pyplot as plt
import threading

class quickplot:
    def __init__(self):
        self.x = []
        self.y = []
        plt.figure()
        plt.ion()
        plt.grid()
        plt.show()
        ax = plt.gca()
        plt.axis('equal')
        plt.xlabel('X Position [m]')
        plt.ylabel('Y Position [m]')
        plt.ylim(-20, 20)
        plt.xlim(-20, 20)

        self.plotting()


    def plotting(self):

            plt.scatter(self.x, self.y)
            plt.pause(.1)
            print(self.x)



