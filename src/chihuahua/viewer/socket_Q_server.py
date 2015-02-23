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
from matplotlib import animation
import numpy as np
import re

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

plt.ion()


class ProcessThread(Thread):
    def __init__(self):
        super(ProcessThread, self).__init__()
        self.running = True
#         self.q = Queue.LifoQueue()
#         self.l=deque()
        self.l=[]
        

        
    def show(self, data): ## add data into the  queue
        self.l.append(data)
        
    def remove(self,idx):
        self.l.pop(idx)
        
    def move(self,idx):
        self.l.pop(idx)    
    
    def list(self):
        print "MQ now is: ",list(self.l)
        return list(self.l)
 
    def stop(self):
        self.running = False
 
    def on_launch(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[])
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.set_xlim(0, 100)
        #Other stuff
        self.ax.grid()


    def on_running(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    
    def run(self):
        q = self.l 
        try:
            # block for 1 second only:
            if len(q)==0:
                print "list is empty!!"
            else:  
                value=q[len(q)-1] #always process latest data in list
                if value["cmd"] == "show" :
                    stock= value["sym"]
#                     starttime=float(value["start"])
#                     stoptime=float(value["end"])
                    interval=float(value["interval"])
#                     ticknum=int((stoptime-starttime)/interval)
                    print "#stock is:",stock
                    to_str_show={"request":{"command":"subscribe", "client": "viewer","symlist":stock}}
                    to_streamer_update={"request":{"command":"update","client":"viewer","interval":"%ss"%interval,"mask":"0111111b","symlist":stock}}
                    input_show=dumps(to_str_show)+"\n"
                    input_update=dumps(to_streamer_update)+"\n"
                a1 = deque([0]*100)
#                 plt.axes(xlim=(0, 10), ylim=(0, 1000))
              
#                 line, = plt.plot(a1)
#                 plt.ion()
#                 plt.show()
#                 plt.close()
                print "begin connect to streamer"
#                 i=1  
                for x in [1]:  # pull and plot the data every second, this is only for real time simulated data
                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # as client for simu     
                    s.connect(("192.168.1.121",8091))
#                     s.connect(("localhost",8091))
                    print "connected to streamer!"
                    print "%sth time: send subscribe request to streamer:" %x,input_show
                    s.send(input_show)
                    print "send out to streamer."
                    s.settimeout(0.5)
                    resp1 = s.recv(1024)
                    print "!!!!!!received simu's response:",resp1
                    sleep(0.5)
                    print "send update command to streamer.."
                    
#                     fig, ax = plt.subplots()
                    self.on_launch()
                    xdata = []
                    ydata = []
                    for x in  np.arange(0,10,1):
                        sleep(0.01)
                        s.send(input_update)
#                         print "recv data1 from streamer.."
                        resp1 = s.recv(1024*10)
#                         print "received simu's data1:",resp1
                    
                        xdata.append(x)
                        
                        rexp = re.compile(r'[^\d.,]+')
                        data=map(float,rexp.sub('', resp1).split(','))[1]
                        ydata.append(data)
#                         print "y:",ydata
#                         print "x:", xdata
                        self.on_running(xdata, ydata)

#                     self.figure.close()
                    
                    
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
 
 
import rpyc 
from rpyc.utils.server import ThreadedServer
class forController(rpyc.Service):
    def exposed_show(self,cmd):
        print "called by controller--- cmd_show"
        thread.show(cmd)    
        thread.run()
        
    def exposed_list(self,cmd):
        print "called by controller--- cmd_show"
        list=thread.list()
        return  list   


def main(): 
    t = ThreadedServer(forController, port = 8090)
    t.start()
    
    
    
    
# def main(): 
#     s = socket.socket()      
#     port = 8090           
#     s.bind(("localhost", port))        # Bind to the port
#     print "Listening on port {p}...".format(p=port)
#  
#     s.listen(5)                 # Now wait for client connection. max q=5
#     while True:
#         try:
#             client, addr = s.accept()
#             ready = select.select([client,],[], [],2)  #wait for I/O complete
#             if ready[0]:
#                 data = client.recv(1024)
#                 data_dict=loads(data)
# #                 print data_dict["cmd"], "<----"
#                 if data_dict["cmd"]=="show":
#                     print "cmd: show"
#                     thread.show(data_dict)    
#                     
#                 elif data_dict["cmd"]=="list":
#                     print  "cmd: list" 
#                     thread.list()
#                     
#                 elif data_dict["cmd"]=="remove":
#                     id=data_dict["id"] 
#                     print  "cmd: remove idx- %s", id 
#                     thread.remove(id)
#                     
#                 elif data_dict["cmd"]=="move":
#                     id=data_dict["id"]
#                     position=data_dict["position"]
#                     print  "cmd: move idx- %s to position- %s",id,position
#                     thread.move(id)
#                     
#                 else:
#                     print "NO valid Command!!!"
#                 
#                                   
#                 print "run now.."
#                 thread.run()
#                 
#         except KeyboardInterrupt:
#             print
#             print "Stop."
#             break
#         except socket.error, msg:
#             print "Socket error!!! %s" % msg
#             break
#     #
#         
#     cleanup()
#  
 
 
def cleanup():
    thread.stop()
    thread.join()
    print thread.isAlive()
 
#########################################################
 
if __name__ == "__main__":
    main()
