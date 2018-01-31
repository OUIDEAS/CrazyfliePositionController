from pymavlink import mavutil
from pymavlink.dialects.v20 import common as mavlink
import struct
import array
import time
import os
import sys
class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)

f = fifo()


mav = mavutil.mavlink_connection('udpin::14551')
#mav = mavutil.mavlink_connection("COM7",baud=115200)
print(mav.address)
print('wait')
mav.wait_heartbeat()
print('got beat')
#print('Set auto')
#mav.set_mode_auto()
#print('Done')

foo = array.array('B',[253, 25, 0, 0, 157, 1, 1, 22, 0, 0, 1, 0, 0, 0, 201, 1, 185, 1, 83, 89, 83, 95, 77, 67, 95, 69, 83, 84, 95, 71, 82, 79, 85, 80, 6, 248, 165])
number = foo[10:14]
numb = struct.unpack('I',number)
# mavl = mavlink.MAVLink(f)
# z=mavl.parse_char(foo)
#x = mavl.decode(foo)
#z = mavl.param_set_encode(param_id=42,param_type=1,param_value=69,target_component=0,target_system=4)
#z = mavlink.MAVLink_param_set_message(param_id=42,param_type=1,param_value=69,target_component=0,target_system=4)
#msg = z.pack(z)

#UDP
#array('B', [253, 25, 0, 0, 137, 1, 1, 22, 0, 0, 2, 0, 0, 0, 232, 1, 164, 0, 77, 65, 86, 95, 84, 89, 80, 69, 0, 0, 0, 0, 0, 0, 0, 0, 6, 223, 39])
#COM
#array('B', [253, 25, 0, 0, 88, 1, 1, 22, 0, 0, 2, 0, 0, 0, 232, 1, 164, 0, 77, 65, 86, 95, 84, 89, 80, 69, 0, 0, 0, 0, 0, 0, 0, 0, 6, 61, 77])


#MAV_COMPONENT
#MAV_COMP_ID_ALL
#mavlink.MAVLink_command_long_message(target_system=0,target_component=0,command=0,confirmation=0,param1=0,param2=0,param3=0,param4=0,param5=0,param6=0,param7=0)
#mav.mav.autopilot_version_send(capabilities=0, flight_sw_version=0, middleware_sw_version=0, os_sw_version=0, board_version=0, flight_custom_version=0, middleware_custom_version=0, os_custom_version=0, vendor_id=0, product_id=0, uid=0)
#mav.mav.message_interval_send(message_id=32, interval_us=0)
#mav.mav.message_interval_send(message_id=32, interval_us=0)
MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES = 520 # Request autopilot capabilities

mav.mav.command_long_send(target_system=1, target_component=1, command=MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES, confirmation=0, param1=1, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0)
while True:
    msg = mav.recv_msg()
    #print(type(msg))
    if msg is not None:
        if msg.name == 'AUTOPILOT_VERSION':
            #print(msg)
            #print ' '.join(format(x, '02x') for x in msg._msgbuf)
            mj = (msg.flight_sw_version >> (8*3)) & 0xFF
            md = (msg.flight_sw_version >> (8*2)) & 0xFF
            mn = (msg.flight_sw_version >> (8*1)) & 0xFF

            print('%i.%i.%i' % (mj,md,mn))
            break
        #else:
            #print(msg)

#VISION_POSITION_ESTIMATE
#LOCAL_POSITION_NED
getparam = ['MAV_TYPE','MAV_SYS_ID','SYS_MC_EST_GROUP','SYS_AUTOSTART','SYS_PARAM_VER']
for ptxt in getparam:
    print(ptxt)
    mav.param_fetch_one(ptxt)

    msg = mav.recv_match(type='PARAM_VALUE', blocking=True)
    #foob = mavlink.MAVLink_autopilot_version_message()
    #foob._msgbuf = msg._msgbuf
    #version = mavlink.MAVLink_autopilot_version_message(msg)
    number = msg._msgbuf[10:14]
    numb = struct.unpack('I', number)
    x=numb[0]
    print(x)
    #print(msg)
    #print(msg._msgbuf)
    #print ' '.join(format(x, '02x') for x in msg._msgbuf)

# 0 start
# 1 length
# 2 sequence
# 3 ID
# 4 component ID
# 5 message ID
# 6 data


#time.sleep(100)
#msg = mavlink.MAVLink_set_home_position_message(target_system=1,altitude=1111,
#                                          latitude=10.0,longitude=4.2,
#                                  q        x=0,y=0,z=0,q=[0, 0, 0, 0],approach_x=0,approach_y=0,approach_z=0)

#this one works
#retval = mav.mav.set_home_position_send(target_system=1,altitude=1111,
#                                          latitude=10.0,longitude=4.2,
#                                          x=0.1,y=0.1,z=0.1,q=[01, 02, 03, 04],approach_x=0,approach_y=0,approach_z=0)
#not sure if actually works because maxproxy does not list the command
#retval = mav.mav.statustext_send(severity=1,text="hello")
#retval = mav.mav.heartbeat_send(type=1,autopilot=1,base_mode=1,custom_mode=1,system_status=1)
#retval = mav.mav.att_pos_mocap_send(q=[4, 5, 6, 7],x=1,y=2,z=3,time_usec=1234)
def main(sysargs):

    import sys, os
    from python_vicon import PyVicon
    import time

    print ("Connecting to Vicon...")
    client = PyVicon()
    client.connect("192.168.10.1", 801)

    if not client.isConnected():
        print ("Failed to connect to Vicon!")
        return 1
    print ("Sending Mocap data")
    csvfiles = []
    csvwriters = {}
    time_usec = 0#time.clock() * 1000 * 1000
    trans_scale = 1000

    print("Sending MAV Vision Data")
    itime_usec=100000
    i=0.01
    dt = 0.1
    while True:
        i=i+0.01
        time.sleep(0.01)#0.05, working
        client.frame()
        subjects = client.subjects()
        for s in subjects:
            if(s=='IRIS_1'):

                trans = client.translation(s)
                if(trans[0] == 0.0 and trans[1] == 0.0 and trans[2] == 0.0):
                    print('dead packet')
                    continue;
                rot = client.rotation(s)
                #rot = [0,0,0]
                #rot[0]=0
                #rot[1]=0
                #rot[2]=0
                q_raw = client.quaternion(s)
                ######message = mav.mav.local_position_ned_send(time_boot_ms=0, x=trans[0]/trans_scale, y=trans[1]/trans_scale, z=trans[2]/trans_scale, vx=0, vy=0, vz=0)
                # ENU (from mocap) | NED new coordinates(in Mavros)
                # x <-----------------------> y = Xned
                # y <-----------------------> x = Yned
                # z <-----------------------> -z = Zned
                x_ENU = trans[0]/trans_scale
                y_ENU = trans[1]/trans_scale
                z_ENU = trans[2]/trans_scale
                x_NED = y_ENU
                y_NED = x_ENU
                z_NED = -z_ENU
                #if (time_usec % 10000 == 0):
                 #   print("%d\t%f\t%f\t%f" % (
                 #   time_usec, x_NED,y_NED,z_NED))
                #ignored by ekf2
                #message = mav.mav.global_vision_position_estimate_send(usec=time_usec,
                #                                                x=x_NED,
                #                                                y=y_NED,
                #                                                z=z_NED,
                #                                                roll=rot[0],
                #                                                pitch=rot[1],
                #                                                yaw=rot[2])

                message = mav.mav.vision_position_estimate_send(usec=time_usec,
                                                                x=x_NED,
                                                                y=y_NED,
                                                                z=z_NED,
                                                                roll=rot[0],
                                                                pitch=rot[1],
                                                                yaw=rot[2])

                #message = mav.mav.vision_speed_estimate_send(usec=time_usec, x=0, y=0, z=0)
                #ignored by ekf2
                #message = mav.mav.vision_position_estimate_send(usec=time_usec,
                #                                                x=trans[0] / trans_scale,
                #                                                y=trans[1] / trans_scale,
                #                                                z=trans[2] / trans_scale, roll=rot[0],
                #                                                pitch=rot[1], yaw=rot[2])
                #message = mav.mav.att_pos_mocap_send(time_usec, q_raw, x=x_NED, y=y_NED, z=z_NED)

        time_usec += 1000
        #itime_usec += dt*1000
        #i=i+0.1
        #print("time %d pos %f"%(itime_usec,i))
        #vision_position_estimate_send
        #usec: Timestamp(microseconds, synced to UNIXtime or since systemboot) (uint64_t)
        #retval = mav.mav.vision_position_estimate_send(x=0, y=0, z=0, usec=itime_usec,roll=0,pitch=0,yaw=0 )

        #retval = mav.mav.global_vision_position_estimate_send(x=i, y=0, z=0, usec=itime_usec,roll=0,pitch=0,yaw=0 )
        ####retval = mav.mav.att_pos_mocap_send(q=[1, 0, 0, 0], x=0, y=0, z=0, time_usec=itime_usec)
        #time.sleep(dt)
        #mav.param_fetch_all()
#i=0
#while True:
#    m = mav.recv_msg()
#    if m is not None:
#        print(m)
#    i=i+1
#    if(i % 10 ==0):
#        retval = mav.mav.att_pos_mocap_send(q=[0, 0, 0, 0], x=0, y=0, z=0, time_usec=1234)

        #while mav.param_fetch_in_progress:
#    print(".")
#    time.sleep(0.5)
#print(retval)
#print(msg)

#mav.write(msg)
#from pymavlink.dialects.v10 import common as mavlink


# create a mavlink instance, which will do IO on file object 'f'
#
# mav = mavlink.MAVLink(f)
#z = mav.recv_msg()
#msg = mav.heartbeat_encode(type=1,autopilot=2,base_mode=0,custom_mode=9,system_status=5)
#msg.pack(mav)
#mav.write(msg)
#print(':'.join(xx.encode('hex') for xx in msg._msgbuf))

#mav = mavlink.MAVLink(f)
#msg = mav.home_position_encode(latitude=33.1234,
#                                               longitude=44.3332,altitude=444,
#                                               x=0,y=1,z=2,q=[1 ,2, 3, 4],approach_x=1,approach_y=2,approach_z=7)
#msg.pack(mav)

#print(':'.join(xx.encode('hex') for xx in msg._msgbuf))

# class fifo(object):
#     def __init__(self):
#         self.buf = []
#     def write(self, data):
#         self.buf += data
#         return len(data)
#     def read(self):
#         return self.buf.pop(0)
#
# f = fifo()
if __name__ == '__main__':
    exit(main(sys.argv))