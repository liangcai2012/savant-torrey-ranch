#! /usr/bin/env python
import socket
import sys
global received
def sendAndReceive():
    global received
    sock.sendall(data + "\n")

    # Receive data from the server and shut down
    received = sock.recv(1024)
    #print "Sent:     {}".format(data)
    print "Received: {}".format(received)
    

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])
data1="1234567890"
for i in range(1000):
    data+=data1

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    
    sendAndReceive()
    
finally:
    sock.close()


