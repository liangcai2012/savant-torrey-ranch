#! /usr/bin/env python
import time
import SocketServer
r= dir(SocketServer)
print(r, SocketServer.__file__)
def showInfo(obj):
    t = type(obj)
    print(t)
class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    g_count = 0

    def handle(self):
        # self.request is the TCP socket connected to the client
        flag = True
        while(flag):
            self.data = self.request.recv(1024).strip()
            
            if(len(self.data)==0):
                if(MyTCPHandler.g_count>800000):
                    MyTCPHandler.g_count =0
                    flag = False
                    print (MyTCPHandler.g_count)
                    
                time.sleep(0.01)
            else:
                #showInfo(self.data)
                MyTCPHandler.g_count +=1
                self.handle_1()
        print("exit loop")
            
                
           
    def handle_1(self):
        if(MyTCPHandler.g_count %100000 == 1):
             print ("{} wrote:".format(self.client_address[0]))
             print (self.data)
            # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())
            

if __name__ == "__main__":
    print("running")
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
