### the server ###
### want the Q always read the last getinto data.
from json import loads,dumps 
import socket,select
import Queue
from collections import deque
from threading import Thread
from time import sleep
# from random import randint
import sys
import matplotlib.pyplot as plt
# import numpy
# import random
# import pylab
# import scipy
# from pandas import *
# from pandas.tools.plotting import plot_frame

# class IndexableQueue(Queue):
#     def __getitem__(self, index):
#         try:
#             self.mutex
#         finally: 
#             return self.queue[index]


class ProcessThread(Thread):
    def __init__(self):
        super(ProcessThread, self).__init__()
        self.running = True
#         self.q = Queue.LifoQueue()
#         self.l=deque()
        self.l=[]
        
    def add(self, data): ## add data into the  queue
        self.l.append(data)
        
    def remove(self,idx):
        self.l.pop(idx)
        
    def move(self,idx):
        self.l.pop(idx)    
    
    def list(self):
        print list(self.l)
 
    def stop(self):
        self.running = False
 
    def run(self):
        q = self.l
#         while self.running:
          
        try:
            # block for 1 second only:
            if len(q)==0:
                print "list is empty!!"
            else:  
                value=q[len(q)-1] #always process latest data in list
                if value["cmd"] == "add" :
                    stock= value["sym"]
                    starttime=float(value["start"])
                    stoptime=float(value["end"])
                    interval=float(value["interval"])
                    ticknum=int((stoptime-starttime)/interval)
                    
                    print stock,starttime,stoptime,interval,ticknum
                    
                
                a1 = deque([0]*100)
                plt.axes(xlim=(0, 10), ylim=(0, 1000))
             

                line, = plt.plot(a1)
                plt.ion()
                plt.show()
                
                 
                i=1  
                for i in [1,2,3]:  # pull and plot the data every second, this is only for real time simulated data
                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # as client for simu     
                    s.connect(("localhost",8091))
                    s.settimeout(1) 
                    print "%s send request to simu:" %i,stock
                    s.send(stock)
                    sleep(1)
                    resp = s.recv(1024)
                    print "received simu's data:",resp
                    
                    a1.appendleft(resp)
                    datatoplot = a1.pop()
                    line.set_ydata(a1)
                    plt.draw()
                    print a1[0]
#                     plt.pause(0.1)
#                     process(resp)
                plt.close()    
                    
        except len(q)==0:
            sys.stdout.write('.')
            sys.stdout.flush()
        #
        if  len(q)>100:
            print "list length is %s, which is larger than 100, remove last one:" %len(q)
            q.pop()
            print list(q)

 
thread = ProcessThread()
thread.start()
 
 
def process(value):  #PULL AND PLOT DATA
    print "process"
    plt.plot(value, 'k--') 
    plt.draw()
    
#     sleep(randint(1,9))    # emulating processing time
 
 
def main():
     
    s = socket.socket()      
    port = 8090           
    s.bind(("localhost", port))        # Bind to the port
    print "Listening on port {p}...".format(p=port)
 
    s.listen(5)                 # Now wait for client connection. max q=5
    while True:
        try:
            client, addr = s.accept()
            ready = select.select([client,],[], [],2)  #wait for I/O complete
            if ready[0]:
                data = client.recv(1024)
                data_dict=loads(data)
#                 print data_dict["cmd"], "<----"
                if data_dict["cmd"]=="add":
                    print "cmd: add"
                    thread.add(data_dict)    
                    
                    
                    
                elif data_dict["cmd"]=="list":
                    print  "cmd: list" 
                    thread.list()
                    
                elif data_dict["cmd"]=="remove":
                    id=data_dict["id"] 
                    print  "cmd: remove idx- %s", id 
                    thread.remove(id)
                    
                elif data_dict["cmd"]=="move":
                    id=data_dict["id"]
                    position=data_dict["position"]
                    print  "cmd: move idx- %s to position- %s",id,position
                    thread.move(id)
                    
                else:
                    print "NO valid Command!!!"
                
                client.close()                  
                thread.run()
                
        except KeyboardInterrupt:
            print
            print "Stop."
            break
        except socket.error, msg:
            print "Socket error! %s" % msg
            break
    #
        
    cleanup()
 
 
 
def cleanup():
    thread.stop()
    thread.join()
 
#########################################################
 
if __name__ == "__main__":
    main()
