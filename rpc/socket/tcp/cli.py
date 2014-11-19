#! /usr/bin/env python
import socket
import sys
import time
class CSocketClient:
    def __init__(self):
        self.__HOST = "localhost"
        self.__PORT = 9999
        self.__dataToSend = ""
        data = ""
        data1="0123456789"
        for i in range(10):
            self.__dataToSend = self.__dataToSend +data1
        print("self.__dataToSend", len(self.__dataToSend))
    def getDataToSend(self):
        return self.__dataToSend
    def connect(self):
         #Create a socket (SOCK_STREAM means a TCP socket)
         self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.__sock.connect((self.__HOST, self.__PORT))
    def close(self):
        self.__sock.close()
    def send(self, data):
        self.__sock.sendall(data)

def test_SocketClient():
    cli = CSocketClient()
    cli.connect()
    data = "1"
    #data = cli.getDataToSend()
    sendcount = 1
    sendcount = 1000*1000
    for i in range(sendcount):
        #data = str(i)
        cli.send(data)
  
def main():
    t1 = time.clock()
    test_SocketClient()
    t2 = time.clock()
    diff = t2-t1
    print(t2, t1, diff)
##    cli.send(data)
##    for i in range(2):
##        cli.send(data)
##        time.sleep(1)
##    cli.close()


main()

