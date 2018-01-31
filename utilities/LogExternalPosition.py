import time



try:
   import zmq
   import json

except ImportError as e:
   raise Exception("ZMQ library probably not installed ({})".format(e))



print ('disconnecting. . .')
zmess ={
 "version": 1,
 "cmd": "disconnect",
 "uri": "radio://0/80/2M"
}
context = zmq.Context()
receiver_cmd = context.socket(zmq.REQ)
bind_addr = "tcp://127.0.0.1:{}".format(2000)
receiver_cmd.connect(bind_addr)
receiver_cmd.send_json(zmess)
response = receiver_cmd.recv()




#Scan for available connections
zmess ={
   "version": 1,
   "cmd": "scan"
}
receiver_cmd.send_json(zmess)
response = receiver_cmd.recv_json()
print(response)
time.sleep(2)


#Connect to radio
zmess ={
 "version": 1,
 "cmd": "connect",
 "uri": "radio://0/80/2M"
}
receiver_cmd.send_json(zmess)
Connection_response = receiver_cmd.recv()
print(Connection_response)



#Create Log Block
zmess = {
  "version": 1,
  "cmd": "log",
  "action": "create",
  "name": "Test log block",
  "period": 1000,
  "variables": [
      "ext_pos.X",
      "ext_pos.Y",
      "ext_pos.Z"
  ]
}
print ('sending log cmd')
receiver_cmd.send_json(zmess)
print ('log cmd sent')
resp = receiver_cmd.recv_json()
print (resp)


#Start the logging
zmess = {
  "version": 1,
  "cmd": "log",
  "action": "start",
  "name": "Test log block"
}

print ('sending log start cmd')
receiver_cmd.send_json(zmess)
print ('log start cmd sent')
resp = receiver_cmd.recv_json()
print (resp)




#Request Log
receiver_log = context.socket(zmq.SUB)
bind_addr = "tcp://127.0.0.1:{}".format(2001)
receiver_log.connect(bind_addr)


try:
    receiver_log.setsockopt_string(zmq.SUBSCRIBE, "")
except:
    receiver_log.setsockopt(zmq.SUBSCRIBE, "")



print('Attemping to receive data... ')
while True:
    message= receiver_log.recv_json()
    print(message["variables"]["ext_pos.X"],"\t",message["variables"]["ext_pos.Y"],"\t",message["variables"]["ext_pos.Z"])


print ('disconnecting. . .')
zmess ={
 "version": 1,
 "cmd": "disconnect",
 "uri": "radio://0/80/1M"
}
receiver_cmd.send_json(zmess)
response = receiver_cmd.recv_json()
print(response)








