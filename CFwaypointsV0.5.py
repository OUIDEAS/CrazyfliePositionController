from cfControlClass import cfControlClass
import threading
import time
import numpy as np
import json
import time
import socket
from python_vicon import PyVicon


#----------------------------------------------------------------------------------------------------------------------
# User Inputs

# Input target points to x and y respectively
Points_x = [0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5]
Points_y = [-0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5]
Points_z = [.75, .75, .75, .75, .75, .75, .75, .75, .75]

# WARNING: CHANGING VSN LIMITS COULD RESULT IN A CRASH!
max_x = 2; min_x = -2
max_y = 2; min_y = -2
max_z = 2; min_z = 0

# specify tolerance range for hitting primary targets
R_tol_primary = 0.06

# add optional wait time at each point to allow for steady state (or 0)
t = 2

# Subdivide input
sub_active = True          # set True or False
R_tol_sub = 0.06            # specify tolerance range for hitting primary targets
doubleCheck_sub = False     # set criterion for massing through sub-points to one check (default) or two check.
dis = False
distance = 0.1                   # set step distance (division distance) in meters
div = True
divisions = 20.0                    # set number of divisions (must include ".0")

#----------------------------------------------------------------------------------------------------------------------
# Check input

if len(Points_y) != len(Points_x) or len(Points_y) != len(Points_z) or len(Points_x) != len(Points_z):
    print("Error: incomplete coordinate group")
    quit()

a = 0; b = 1

while b <= len(Points_x):

    if Points_x[a] > max_x or Points_x[a] < min_x:
        print("Error: set points outside safe range")
        quit()

    if Points_y[a] > max_y or Points_y[a] < min_y:
        print("Error: set points outside safe range")
        quit()

    if Points_z[a] > max_z or Points_z[a] < min_z:
        print("Error: set points outside safe range")
        quit()

    a = a + 1; b = b + 1

if sub_active == True and dis == True and div == True:
    print("Error: You cannot creat subpoints by distance AND number of divisions. You must choose one option")
    quit()

if sub_active == True and dis == False and div == False:
    print("Error: Subpoints must be created by either distance OR number of divisions.")
    quit()

#----------------------------------------------------------------------------------------------------------------------
#logName is WayPts_(CF#)_(max x, max y, z)
uav = cfControlClass(uavName='CF',dispUpdateRate=False,logEnabled=True,logName='WayPts_sub_10_2(5)',dispMessageMonitor=True)
time.sleep(2)

#----------------------------------------------------------------------------------------------------------------------
#save settings
filehandle = open('settings_sub_2(5).txt', 'a')
i = 0
j = 0
k = 0

filehandle.write('Points_x:')
while i < len(Points_x):
    filehandle.write(repr(Points_x[i]) + ', ')
    i = i+1
filehandle.write('\n')

filehandle.write('Points_y:')
while j < len(Points_x):
    filehandle.write(repr(Points_y[j]) + ', ')
    j = j+1
filehandle.write('\n')

filehandle.write('Points_y:')
while k < len(Points_x):
    filehandle.write(repr(Points_y[k]) + ', ')
    k = k+1
filehandle.write('\n')

filehandle.write('\n' + 'Primary point range tollerance:' + repr(R_tol_primary) + '\n')
filehandle.write('Primary point sleep time:' + repr(t) + '\n')

if sub_active == True:
    filehandle.write('\n' + 'Subpoint settings:' + '\n')
    filehandle.write('\t' + 'Subpoint range tollerance:' + repr(R_tol_sub) + '\n')
    if doubleCheck_sub == True:
        filehandle.write('\t' + 'Subpoints are using two-check system.' + '\n')
    else:
        filehandle.write('\t' + 'Subpoints are using one-check system.' + '\n')
    if dis == True:
        filehandle.write('\t' + 'Division distance:' + repr(distance) + '\n')
    elif div == True:
        filehandle.write('\t' + 'Number of divisions:' + repr(divisions) + '\n')
else:
    filehandle.write('Subpoints not used')

filehandle.close()

#----------------------------------------------------------------------------------------------------------------------
# Subdivide
i = 0
j = 0
a = 0
b = 0
c = 0
Xsub = []
Ysub = []
Zsub = []

if sub_active == True:
    print("Generating sub-setpoints...")

    while True:
        # x points are used but you could also use y or z
        if i < len(Points_x) - 1:
            if dis == True:
                distance_x = distance_y = distance_z = distance
                num_subPts_x = (abs(Points_x[i] - Points_x[i + 1])) / distance_x
                num_subPts_y = (abs(Points_y[i] - Points_y[i + 1])) / distance_y
                num_subPts_z = (abs(Points_z[i] - Points_z[i + 1])) / distance_z

                if num_subPts_x.is_integer() == False or num_subPts_y.is_integer() == False or num_subPts_x.is_integer() == False:
                    num_subPts_xround = round(num_subPts_x)
                    num_subPts_yround = round(num_subPts_y)
                    num_subPts_zround = round(num_subPts_z)
                    print("Warning: Number of divisions is not an integer value. This may result in issues during flight. Try changing the value 'div'.")
                    print("Quit in 10 seconds or program will continue.")
                    time.sleep(10)

                if num_subPts_x == 0 and num_subPts_y == 0 and num_subPts_z == 0:
                    print("Error: You cannot have two or more consecutive setpoitns at the same coordinates.")
                    quit()

                if num_subPts_x == 0 and num_subPts_y != 0:
                    num_subPts_x = num_subPts_y

                if num_subPts_y == 0 and num_subPts_x != 0:
                    num_subPts_y = num_subPts_x

                if num_subPts_x == 0 and num_subPts_y == 0 and num_subPts_z != 0:
                    num_subPts_x = num_subPts_z
                    num_subPts_y = num_subPts_z

                if num_subPts_z == 0 and num_subPts_x != 0:
                    num_subPts_z = num_subPts_x

                if num_subPts_z == 0 and num_subPts_y != 0:
                    num_subPts_z = num_subPts_y

            elif div == True:
                num_subPts_x = divisions
                num_subPts_y = divisions
                num_subPts_z = divisions

                if divisions.is_integer() == False:
                    print("Error: number of subpoints must be an integer value.")
                    quit()

                if num_subPts_x == 0 and num_subPts_y == 0 and num_subPts_z == 0:
                    print("Error: You cannot have two or more consecutive setpoitns at the same coordinates.")
                    quit()

                if (abs(Points_x[i] - Points_x[i + 1])) == 0:
                    distance_x = 0
                else:
                    distance_x = (abs(Points_x[i] - Points_x[i + 1])) / num_subPts_x

                if (abs(Points_y[i] - Points_y[i + 1])) == 0:
                    distance_y = 0
                else:
                    distance_y = (abs(Points_y[i] - Points_y[i + 1])) / num_subPts_y

                if (abs(Points_z[i] - Points_z[i + 1])) == 0:
                    distance_z = 0
                else:
                    distance_z = (abs(Points_z[i] - Points_z[i + 1])) / num_subPts_z

            j = 0
            while j < num_subPts_x:
                if Points_x[i] == Points_x[i+1]:
                    Xsub.insert(a, Points_x[i])

                elif Points_x[i] < Points_x[i+1]:
                    X_sub = Points_x[i] + distance_x * j
                    Xsub.insert(a, X_sub)

                elif Points_x[i] > Points_x[i+1]:
                    X_sub = Points_x[i] - distance_x * j
                    Xsub.insert(a, X_sub)

                # filehandle = open('x_sub.txt', 'a')
                # filehandle.write('\n' + repr(Xsub[a]))
                # filehandle.close()

                j = j + 1
                a = a + 1

            j = 0
            while j < num_subPts_y:
                if Points_y[i] == Points_y[i + 1]:
                    Ysub.insert(b, Points_y[i])

                elif Points_y[i] < Points_y[i + 1]:
                    Y_sub = Points_y[i] + distance_y * j
                    Ysub.insert(b, Y_sub)

                elif Points_y[i] > Points_y[i + 1]:
                    Y_sub = Points_y[i] - distance_y * j
                    Ysub.insert(b, Y_sub)

                # filehandle = open('y_sub.txt', 'a')
                # filehandle.write('\n' + repr(Ysub[b]))
                # filehandle.close()

                j = j + 1
                b = b + 1

            j = 0
            while j < num_subPts_z:
                if Points_z[i] == Points_z[i+1]:
                    Zsub.insert(c, Points_z[i])

                elif Points_z[i] < Points_z[i+1]:
                    Z_sub = Points_z[i] + distance_z * k
                    Zsub.insert(c, Z_sub)

                elif Points_z[i] > Points_z[i+1]:
                    Z_sub = Points_z[i] - distance_z * k
                    Zsub.insert(c, Z_sub)

                # filehandle = open('z_sub.txt', 'a')
                # filehandle.write('\n' + repr(Zsub[c]))
                # filehandle.close()

                j = j + 1
                c = c + 1

            i = i + 1

        else:
            print("Sub-setpoints created")
            break

#----------------------------------------------------------------------------------------------------------------------
# Subdivide

# Initialize variables
i = 0
j = 0
k = 0
Range_sub = []
Range2 = []

if sub_active == True:

    while uav.active:

        uav.takeoff(Points_z[0])
        time.sleep(t)

        while True:

            X = uav.QueueList["vicon_utility"].get()
            x_prev = X["x"]
            y_prev = X["y"]
            z_prev = X["z"]

            R1 = np.sqrt((x_prev - Xsub[i]) ** 2 + (y_prev - Ysub[i]) ** 2 + (z_prev - Zsub[i]) ** 2)
            Range_sub.insert(j, R1)

            R2 = np.sqrt((x_prev - Points_x[k]) ** 2 + (y_prev - Points_y[k]) ** 2 + (z_prev - Points_z[k]) ** 2)
            Range2.insert(j, R2)

            if j == 0:  # if this is the first one set the point. This has to be done this way!
                uav.goto(Xsub[i], Ysub[i], Zsub[i])
                time.sleep(t)

            if (R1 <= R_tol_sub) and (R2 > R_tol_primary):
                if doubleCheck_sub == True:
                    if j >= 1:
                        if Range_sub[j] > Range_sub[j - 1]:
                            i = i + 1  # move to next target
                            uav.goto(Xsub[i], Ysub[i], Zsub[i])

                if doubleCheck_sub == False:
                    i = i + 1
                    if i == len(Xsub):
                        # if drone is within range of the final target this shuts it down
                        uav.land()
                        print('landing')
                        time.sleep(5)
                        break
                    else:
                        uav.goto(Xsub[i], Ysub[i], Zsub[i])

            if R2 <= R_tol_primary:
                if j >= 1:
                    if Range2[j] > Range2[j - 1]:
                        #if it gets into here, that means its reached a primary point, even though subpoints must still be used in the goto.
                        k = k + 1  # move to next target
                        uav.goto(Xsub[i], Ysub[i], Zsub[i])
                        time.sleep(t)

            j = j + 1

        uav.cf_vicon.active = False
        time.sleep(0.25)
        uav.active = False

#----------------------------------------------------------------------------------------------------------------------
# Primary points only

# Initialize variables
i = 0
j = 0
Range = []

if sub_active == False:

    while uav.active:

        uav.takeoff(Points_z[0])
        time.sleep(t)

        while True:

            X = uav.QueueList["vicon_utility"].get()
            x_prev = X["x"]
            y_prev = X["y"]
            z_prev = X["z"]

            R = np.sqrt((x_prev - Points_x[i]) ** 2 + (y_prev - Points_y[i]) ** 2 + (z_prev - Points_z[i]) ** 2)
            Range.insert(j, R)

            if j == 0: # if this is the first one set the point. This has to be done this way!
                uav.goto(Points_x[i], Points_y[i], Points_z[i])
                time.sleep(t)

            if R <= R_tol_primary:
                if i + 1 == len(Points_x):
                    # if drone is within range of the final target this shuts it down
                    uav.land()
                    print('landing')
                    time.sleep(5)
                    break

                if j >= 1:
                    if Range[j] > Range[j - 1]:
                        i = i + 1  # move to next target
                        uav.goto(Points_x[i], Points_y[i], Points_z[i])
                        time.sleep(t)

            j = j + 1

        uav.cf_vicon.active = False
        time.sleep(0.25)
        uav.active = False

print('dead')
quit()