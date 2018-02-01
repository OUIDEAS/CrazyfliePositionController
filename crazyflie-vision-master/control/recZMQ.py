import zmq


context = zmq.Context()
vicon_conn = context.socket(zmq.PULL)
result = vicon_conn.bind("tcp://127.0.0.1:7777")

while True:
    message = vicon_conn.recv_json()
    print(message)