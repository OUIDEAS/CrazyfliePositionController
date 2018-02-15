import time
from viconStream import viconStream


example = viconStream('CF_3')


time.sleep(2)
while True:
    # print("data")
    print(example.X["z"])
    time.sleep(1)


