# Lost track of the working Dubins UAV example I had...so this file is to make sure I understand how my own class works



from matplotlib import pyplot as plt
from vectorField import vectorField as vf
from dubinsUAV import dubinsUAV as duav



velocity = 0.25
#Determine these values from MATLAB
m = 1
y_ratio = 0.5
k = 2.0
Ho = -3.3
theta_r = velocity/0.35

VF = vf(m,y_ratio,k,Ho,theta_r,velocity)
VF.calcFullField()

VF.simulateDubins(velocity)

# plt.quiver(VF.Xs,VF.Ys,VF.Us,VF.Vs)
# VF.pltObstacle()
# plt.axis('equal')
# plt.show()
plt.pause(100000)
