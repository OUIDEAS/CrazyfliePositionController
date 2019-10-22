import numpy as np
import time
from pid import PID_RP
import threading

import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig

from threading import Thread

class PID_CLASS():
    def __init__(self, link_uri, QueueList = {}, name = ''):

        self.time_start = time.time()
        self.name = name

        self.QueueList = QueueList

        # ZMQ controller
        # self.context = zmq.Context()
        # self.client_conn = self.context.socket(zmq.PUSH)
        # self.client_conn.connect("tcp://127.0.0.1:1212")

        self.message = {}
        self.message["mess"] = None
        self.message["data"] = None

        # Change from string to correct variable types!!!!!!!!!!!!!!!!!!!!!!
        # Also at some point fix the delay in data with crazyflie
        self.CF_roll = "NaN"
        self.CF_pitch = "NaN"
        self.CF_yaw = "NaN"
        self.CF_thrust = "NaN"
        self.CF_Xacc = "NaN"
        self.CF_Yacc = "NaN"
        self.CF_Zacc = "NaN"

        # Crazyflie connection from ramp.py:
        self._cf = Crazyflie(rw_cache='./cache')

        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        print('Connecting to %s' % link_uri)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

        # # Variable used to keep main loop occupied until disconnect
        # self.is_connected = True

        t = threading.Thread(target=self.run,args=(QueueList,),name="PID")
        t.daemon = True
        t.start()

    # Connection Functions in ramp.py
    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)
        # Add in the logging variables here?
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
        self._lg_stab.add_variable('stabilizer.roll', 'float')
        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')
        self._lg_stab.add_variable('stabilizer.thrust', 'uint16_t')
        self._lg_stab.add_variable('acc.x', 'float')
        self._lg_stab.add_variable('acc.y', 'float')
        self._lg_stab.add_variable('acc.z', 'float')
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback froma the log API when data arrives"""
        # print('[%d][%s]: %s' % (timestamp, logconf.name, data))
        self.CF_roll = data["stabilizer.roll"]
        self.CF_pitch = data["stabilizer.pitch"]
        self.CF_yaw = data["stabilizer.yaw"]
        self.CF_thrust = data["stabilizer.thrust"]
        self.CF_Xacc = data["acc.x"]
        self.CF_Yacc = data["acc.y"]
        self.CF_Zacc = data["acc.z"]

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)

    def disconnect(self):
        print("Maybe Disconnecting from Crazyflie...")
        time.sleep(.2)
        self._cf.close_link

    def my_map(self, x, in_min, in_max, out_min, out_max):
        # for converting thrust from percent to 0 - 65535
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


    def run(self, QueueList):
        # Options
        self.dispControlMessage = False

        self.sleep_rate = 0.005
        self.update_rate = []

        self.cmd = {
            "version": 1,
            "client_name": "N/A",
            "ctrl": {
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": 0.0,
                "thrust": 0.0
            }
        }

        if QueueList["controlShutdown"].empty():
            active = True
            self.SPx = 0
            self.SPy = 0
            self.SPz = 0
            self.SP_yaw = 0

            self.x = 0
            self.y = 0
            self.z = 0
            self.yaw = 0

            # self.client_conn.send_json(self.cmd)
            # CF library commands (roll, pitch, yaw, thrust)
            # self._cf.commander.send_setpoint(self.cmd["ctrl"]["roll"], self.cmd["ctrl"]["pitch"],
            #                                  self.cmd["ctrl"]["yaw"], self.cmd["ctrl"]["thrust"])
            self._cf.commander.send_setpoint(0, 0, 0, 0)

            self.message["mess"] = 'MOTOR_UNLOCK_SENT'
            self.message["data"] = self.name
            self.QueueList["threadMessage"].put(self.message)

            time.sleep(1)
            # Controller gain default values
            self.rPID_P = 25
            self.rPID_I = 25
            self.rPID_D = 35
            self.rPID_set_point = 0

            self.pPID_P = 40
            self.pPID_I = 25
            self.pPID_D = 45
            self.pPID_set_point = 0

            self.yPID_P = 80
            self.yPID_I = 50
            self.yPID_D = 30

            # self.tPID_P = 70
            self.tPID_P = 100
            # self.tPID_I = 100
            self.tPID_I = 90
            # self.tPID_D = 100
            self.tPID_D = 70
            self.tPID_set_point = 0

            # Setup PID controllers
            # zmq connection?
            self.r_pid = PID_RP(name="roll", P=self.rPID_P, I=self.rPID_I, D=self.rPID_D, Integrator_max=15,
                                Integrator_min=-15, set_point=0,
                                zmq_connection=0)
            self.p_pid = PID_RP(name="pitch", P=self.pPID_P, I=self.pPID_I, D=self.pPID_D, Integrator_max=15,
                                Integrator_min=-15, set_point=0,
                                zmq_connection=0)
            self.y_pid = PID_RP(name="yaw", P=self.yPID_P, I=self.yPID_I, D=self.yPID_D, Integrator_max=10,
                                Integrator_min=-5, set_point=0,
                                zmq_connection=0)
            self.t_pid = PID_RP(name="thrust", P=self.tPID_P, I=self.tPID_I, D=self.tPID_D, set_point=0,
                                Integrator_max=120,
                                Integrator_min=-120, zmq_connection=0)

            SPx = 0
            SPy = 0
            SPz = 0
            SP_yaw = 0

        else:
            active = False
            self.kill()

        for i in range(0,QueueList["vicon"].qsize()):
            #Clear vicon Q before starting
            QueueList["vicon"].get()

        X = QueueList["vicon"].get()
        x_prev = X["x"]
        y_prev = X["y"]
        z_prev = X["z"]

        while active:

            t1 = time.time()
            try:

                # print(QueueList["vicon"].qsize())

                if QueueList["vicon"].full():
                    pass

                try:
                    X = QueueList["vicon"].get()

                except:
                    self.message["mess"] = 'VICON_QUEUE_EXCEPTION_ERROR'
                    self.message["data"] = self.name
                    self.QueueList["threadMessage"].put(self.message)
                    self.kill()
                    return

                x = X["x"]
                y = X["y"]
                z = X["z"]
                yaw = X["yaw"]
                yawRate = X["yawRate"]


                if not QueueList["sp"].empty():
                    new_set_point = QueueList["sp"].get()

                    SPx = new_set_point["x"]
                    SPy = new_set_point["y"]
                    SPz = new_set_point["z"]

                    self.message["mess"] = 'NEW_SP_ACCEPTED'
                    self.message["data"] = new_set_point
                    self.QueueList["threadMessage"].put(self.message)

                # Changing setpoint to local coordinates
                theta = np.arctan2(SPy - y, SPx - x)
                SPx_b = SPx - x
                SPy_b = SPy - y
                range_to_sp = np.sqrt(np.square(SPx_b) + np.square(SPy_b))
                xa = range_to_sp * np.cos(theta)
                ya = range_to_sp * np.sin(theta)

                # Calculate set point locations relative to the UAV frame
                xb = xa * np.cos(yaw) + ya * np.sin(yaw)
                yb = -xa * np.sin(yaw) + ya * np.cos(yaw)

                # Assign the relative set-point
                self.r_pid.set_point = xb - x
                self.p_pid.set_point = yb - y
                self.y_pid.set_point = self.SP_yaw - yaw
                self.t_pid.set_point = SPz


                #Update controller
                roll = self.r_pid.update(-x)
                pitch = self.p_pid.update(-y)
                thrust = self.t_pid.update(z)
                yaw_cmd = self.y_pid.update(yaw)


                # Saturation control
                pitch_roll_cap = 20

                if thrust > 100:
                    thrust = 100
                elif thrust < 0:
                    thrust = 0
                if abs(pitch) > pitch_roll_cap:
                    pitch = np.sign(pitch) * pitch_roll_cap
                if abs(roll) > pitch_roll_cap:
                    roll = np.sign(roll) * pitch_roll_cap

                #Lock variables, update message
                self.cmd["ctrl"]["roll"] = -roll
                self.cmd["ctrl"]["pitch"] = -pitch
                #self.cmd["ctrl"]["thrust"] = thrust
                self.cmd["ctrl"]["thrust"] = self.my_map(thrust,0,100,0,65535)
                self.cmd["ctrl"]["yaw"] = -yaw_cmd


                # self.client_conn.send_json(self.cmd,zmq.NOBLOCK)
                # self.client_conn.send_json(self.cmd)
                # time.sleep(self.sleep_rate)

                # CF library commands (roll, pitch, yaw, thrust)
                self._cf.commander.send_setpoint(self.cmd["ctrl"]["roll"], self.cmd["ctrl"]["pitch"],
                                                  self.cmd["ctrl"]["yaw"], self.cmd["ctrl"]["thrust"])

                if self.dispControlMessage:
                    print("Roll:", "{0:.3f}".format(self.cmd["ctrl"]["roll"]), "\t","Pitch:", "{0:.3f}".format(self.cmd["ctrl"]["pitch"]),
                          "\t","Yaw:", "{0:.3f}".format(self.cmd["ctrl"]["yaw"]), "\t","Thrust:", "{0:.3f}".format(self.cmd["ctrl"]["thrust"]))

                t2 = time.time()

                self.update_rate = 1 / (t2 - t1)


                #Calculate speed of UAV
                u = np.sqrt(((X["x"]-x_prev)*self.update_rate)**2+((X["y"]-y_prev)*self.update_rate)**2+((X["z"]-z_prev)*self.update_rate)**2)
                x_prev = X["x"]
                y_prev = X["y"]
                z_prev = X["z"]

                # Datalogger contents
                pkt = {
                    "time":time.time()-self.time_start,
                    "x": x,
                    "y": y,
                    "z": z,
                    "yaw": yaw,
                    "velocity": u,
                    "x_sp": SPx,
                    "y_sp": SPy,
                    "z_sp": SPz,
                    "yaw_sp": SP_yaw,
                    "Roll_cmd": self.cmd["ctrl"]["roll"],
                    "Pitch_cmd": self.cmd["ctrl"]["pitch"],
                    "Thrust_cmd": self.cmd["ctrl"]["thrust"],
                    "Yaw_cmd": self.cmd["ctrl"]["yaw"],
                    "Roll": self.CF_roll,
                    "Pitch": self.CF_pitch,
                    "Yaw_CF": self.CF_yaw,
                    "Thrust": self.CF_thrust,
                    "X_acc": self.CF_Xacc,
                    "Y_acc": self.CF_Yacc,
                    "Z_acc": self.CF_Zacc,
                }

                self.QueueList["dataLogger"].put_nowait(pkt)

                if not self.QueueList["controlShutdown"].empty():
                    if self.QueueList["controlShutdown"].get() == 'THROTTLE_DOWN':
                        self.throttleDown()
                        active = False
                    else:
                        self.kill()
                    return

                # if not logQ.full():
                #     logQ.put(pkt)
                # print(self.update_rate)
            except Exception as ex:
                print(ex)

    def kill(self):

        self.message["mess"] = 'ATTEMPTING_TO_SEND_KILL_CMD'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)

        self.sentKill = False
        while not self.sentKill:
            try:
                self.cmd["ctrl"]["roll"] = 0
                self.cmd["ctrl"]["pitch"] = 0
                self.cmd["ctrl"]["thrust"] = 0
                self.cmd["ctrl"]["yaw"] = 0


                # self.client_conn.send_json(self.cmd,zmq.NOBLOCK)

                # CF library commands (roll, pitch, yaw, thrust)
                self._cf.commander.send_setpoint(self.cmd["ctrl"]["roll"], self.cmd["ctrl"]["pitch"],
                                                 self.cmd["ctrl"]["yaw"], self.cmd["ctrl"]["thrust"])

                self.message["mess"] = 'KILL_CMD_SENT'
                self.message["data"] = self.name
                self.QueueList["threadMessage"].put(self.message)

                self.sentKill = True
            except:
                pass
        # Disconnect from crazyflie
        self.disconnect()


    def throttleDown(self):

        self.message["mess"] = 'THROTTLE_DOWN_START'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)
        time.sleep(0.01)


        self.cmd["ctrl"]["roll"] = 0
        self.cmd["ctrl"]["pitch"] = 0
        self.cmd["ctrl"]["yaw"] = 0

        # if self.cmd["ctrl"]["thrust"]>50:
        #     self.cmd["ctrl"]["thrust"] = 50

        if self.cmd["ctrl"]["thrust"]>32767:
            self.cmd["ctrl"]["thrust"] = 32767


        while self.cmd["ctrl"]["thrust"] > 0:
            # self.cmd["ctrl"]["thrust"] = self.cmd["ctrl"]["thrust"]-1
            self.cmd["ctrl"]["thrust"] = self.cmd["ctrl"]["thrust"]-500
            # self.client_conn.send_json(self.cmd, zmq.NOBLOCK)

            # CF library commands (roll, pitch, yaw, thrust)
            self._cf.commander.send_setpoint(self.cmd["ctrl"]["roll"], self.cmd["ctrl"]["pitch"],
                                             self.cmd["ctrl"]["yaw"], self.cmd["ctrl"]["thrust"])

            time.sleep(0.05)


        self.message["mess"] = 'THROTTLE_DOWN_COMPLETE'
        self.message["data"] = self.name
        self.QueueList["threadMessage"].put(self.message)

        return
