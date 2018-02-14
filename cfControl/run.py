from plots import responsePlots
import time
import numpy as np

plot = responsePlots()

while True:
    t = time.time()-plot.ts
    x = np.cos(t)
    y = np.sin(t)
    z = 1
    time.sleep(0.01)

    pkt = {
        "x": x,
        "y": y,
        "z": z,
        "yaw": y,
        "x_sp": 1,
        "y_sp": y,
        "z_sp": y,
        "yaw_sp": y,
    }

    plot.update_plots(pkt)