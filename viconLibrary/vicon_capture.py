import sys
from python_vicon import PyVicon

def main(sysargs):
    
    # open Vicon connection
    print ("Connecting to Vicon...")
    client = PyVicon()
    ip_address = '192.168.10.1'
    port = 801
    client.connect(ip_address, port)
    
    if not client.isConnected():
        print ("Failed to connect to Vicon! {}:{}".format(
                                            ip_address, port))
        return 1
    
    
    client.frame()
    subjects = client.subjects()
    # main loop
    while True:
        client.frame()
        for s in subjects:
            print('data')
     
    client.disconnect()
    
    print ("\nComplete.")
    return 0

if __name__ == '__main__':
    exit(main(sys.argv))
