#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2013 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.

import math

import zmq

import time

class PID:

    def __init__(self, name="N/A", P=1.0, I=0.0, D=10.0, Derivator=0, Integrator=0,
                 Integrator_max=300, Integrator_min=-200, set_point=0.0,
                 power=1.0, zmq_connection=None):
        self._zmq = zmq_connection
        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.Derivator=Derivator
        self.power = power
        self.Integrator=Integrator
        self.Integrator_max=Integrator_max
        self.Integrator_min=Integrator_min
        self.last_error = 0.0
        self.last_value = 0.0

        self.set_point=set_point
        self.error=0.0


        self._z_data = {
            "name": name,
            "data": {
                "P": 0.1,
                "I": 0.1,
                "D": 0.0,
                "E": 0.0,
                "SP": 0.0,
            }
        }


    def update(self,current_value):
        """
        Calculate PID output value for given reference input and feedback
        """

        self.error = self.set_point - current_value

        self.P_value = self.Kp * self.error
        if (self.last_value >= current_value):
            change = self.error - self.last_error
        else:
            change = 0.0

        if self.error > 0.0:
            self.I_value = self.Integrator * self.Ki
        else:
            self.I_value = (self.Integrator * self.Ki)


        #self.D_value = self.Kd * ( self.error - self.Derivator)
        self.D_value = self.Kd * change
        self.Derivator = self.error

        self.Integrator = self.Integrator + self.error

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min

        self.last_error = self.error
        self.last_value = current_value

        PID = self.P_value + self.I_value + self.D_value

        self._z_data["data"]["P"] = self.P_value
        self._z_data["data"]["I"] = self.I_value
        self._z_data["data"]["D"] = self.D_value
        self._z_data["data"]["E"] = self.error
        self._z_data["data"]["SP"] = self.set_point
        self._z_data["data"]["OUT"] = PID

        if self._zmq:
            try:
                self._zmq.send_json(self._z_data, zmq.NOBLOCK)
            except zmq.error.Again:
                pass

        return PID

    def set_point(self,set_point):
        """Initilize the setpoint of PID"""
        self.set_point = set_point
        self.Integrator=0
        self.Derivator=0

class PID_RP:

    def __init__(self, name="N/A", P=1.0, I=0.0, D=10.0, Derivator=0, Integrator=0,
                 Integrator_max=20000, Integrator_min=-20000, set_point=0.0,
                 power=1.0, zmq_connection=None):

        self._zmq = zmq_connection
        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.name = name
        self.Derivator=Derivator
        self.power = power
        self.Integrator=Integrator
        self.Integrator_max=Integrator_max
        self.Integrator_min=Integrator_min
        self.last_error = 0.0
        self.last_value = 0.0

        self.set_point=set_point
        self.error=0.0

        self.prev_t = 0

        self._z_data = {
            "name": name,
            "data": {
                "P": 0.0,
                "I": 0.0,
                "D": 0.0,
                "E": 0.0,
                "SP": 0.0,
                "OUT": 0.0
            }
        }

    def reset_dt(self):
        self.prev_t = time.time()

    def update(self, current_value):
        """
        Calculate PID output value for given reference input and feedback
        """

        dt = (time.time() - self.prev_t)
        self.prev_t = time.time()
        self.error = self.set_point - current_value

        self.P_value = self.Kp * self.error
        change = self.error - self.last_error

        self.I_value = self.Integrator * self.Ki * dt

        #self.D_value = self.Kd * ( self.error - self.Derivator)
        self.D_value = self.Kd * change / dt
        self.Derivator = self.error

        self.Integrator = self.Integrator + self.error

        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min

        self.last_error = self.error
        self.last_value = current_value

        #print "{}: P={}, I={}, D={}".format(self.name, self.P_value, self.I_value, self.D_value)

        PID = self.P_value + self.I_value + self.D_value

        self._z_data["data"]["P"] = self.P_value
        self._z_data["data"]["I"] = self.I_value
        self._z_data["data"]["D"] = self.D_value
        self._z_data["data"]["E"] = self.error
        self._z_data["data"]["SP"] = self.set_point
        self._z_data["data"]["OUT"] = PID

        if self._zmq:
            try:
                self._zmq.send_json(self._z_data, zmq.NOBLOCK)
            except zmq.error.Again:
                pass

        return PID

    def set_point(self,set_point):
        """
        Initilize the setpoint of PID
        """
        self.set_point = set_point
        self.Integrator=0
        self.Derivator=0
