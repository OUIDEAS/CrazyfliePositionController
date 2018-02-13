from fakeVicon import *
from quickplot import *
import matplotlib.pyplot as plt
import threading



def plotting():
    time.sleep(1)
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
    while True:
        plt.scatter(x, y)
        plt.pause(.1)


x = []
y = []
FV = fakeVicon()
print("starting print thread")
threading.Thread(target=plotting(),args=(x,y)).start()
print("print thread started")

for i in range(0,100,1):
    [x,y,z,heading] = FV.getData()
    print(i)
    time.sleep(1)



