

from viconStream import viconStream
from multiprocessing import Queue

QueueList = {}
QueueList["vicon"] = Queue(maxsize=20)
QueueList["vicon_utility"] = Queue(maxsize=2)
QueueList["threadMessage"] = Queue()



name = 'dummy'
fakeVicon = False

cf_vicon = viconStream(name ,QueueList ,fakeVicon)

while True:
    X = QueueList["vicon"].get()
    print(X)