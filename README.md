# Crazyflie Position Control and Guidance

Python library for controlling the position of the crazyflie 2.0. 

# Requirements
- Python 3.6
- Python vicon built for python 3.x
- Crazyflie Client with ZMQ input enabled

# Program Structure

![alt text](/Documentation/flowchart.PNG)
- main.py is intended to be a high level command script for controlling the crazyflie
	- uav.takeoff(altitude)
	- uav.goto(x,y,z)
	- uav.land()

- cfControlClass.py creates a queue list for communication and starts up threads
	- self.startVicon() spawns vicon thread that captures self.name position data
	- self.startControl() spawns control thread that outputs (R,P,Y,T) commands to cfClient based on current position and set-points
	- self.startLog() spawns log thread that writes data from the PID thread to a .txt file
	- Other threads can be easily added to the class and passed the QueueList dict for passing vicon data, set-points, etc

- viconStream.py collects position data from vicon system
	- fake data can be used by setting fakeVicon arg to True
	- Position data is .put into two queues
		- ["vicon"] intended ONLY for PID. Do NOT .get() data from ["vicon"] queue for other threads, use ["vicon_utility"]

- PID_CLASS.py sends ZMQ messages to cfclient for controlling position
	- Accepts set-point messages from ["sp"] queue
	- Pulls position data from ["vicon"] queue
	- Outputs a dict to ["dataLogger"] queue for logging




# Instructions:
- cd inside cfControl folder
- For new scripts, import cfControlClass
- See demo.py for example
 

# Known problems and future improvements
- Geofence
- Rollover protection
- Landing velocity control
- Takeoff veloocity control
- Guidance selector
- Sub to crazyflie and log
