### the server ###
### want the Q always read the last getinto data.
from json import loads,dumps 
import socket,select
# import Queue
from collections import deque
from threading import Thread,Event
from time import sleep
import time
# from random import randint
import sys
import matplotlib.pyplot as plt
# from matplotlib import animation
import numpy as np
import re
import rpyc 
from rpyc.utils.server import ThreadedServer

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
l=[]
to_str_show={"request":{"command":"subscribe", "client": "viewer","symlist":["QQQ","SPY"]}}
to_streamer_update={"request":{"command":"update","client":"viewer","interval":"1s","mask":"0111111b","symlist":["QQQ","SPY"]}}
xdata = {"1":[],"2":[]}
ydata = {"1":[],"2":[]}
       
        
class recvdata(Thread):
    def __init__(self,event):
        super(recvdata, self).__init__()
        self.running = True
        self.stopped = event
        global l,xdata,ydata
        self.x=0  
          
    def connect(self):
        global to_str_show
        global to_streamer_update
        self.input_show=dumps(to_str_show)+"\n"
        self.input_update=dumps(to_streamer_update)+"\n"
        
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # as client for simu     
#                     s.connect(("192.168.1.121",8091))
        self.s.connect(("localhost",8091))
        print "connected to streamer!"
        print "send subscribe request to streamer: %s" %self.input_show
        self.s.send(self.input_show)
        sleep(1)
        print "have done send out"
        thread2.on_launch()
        print "launch plot now..."


    def streaming(self):
        next_call = time.time() 
        while not self.stopped.wait(next_call - time.time()):  #timer compensate

            self.x=self.x+1
            self.s.send(self.input_update)
            print "have sent update command to streamer.."
        #                         print "recv data1 from streamer.."
            resp1 = self.s.recv(1024*10)
        #                         print "received simu's data1:",resp1
            print "received data from streamer!!"
            xdata["1"].append(self.x)
            xdata["2"].append(self.x)
        #             print resp1,"dd"
            resp_A=resp1.split('\n')[0]
            resp_B=resp1.split('\n')[1]
            
            rexp = re.compile(r'[^\d.,]+')
            data1=map(float,rexp.sub('', resp_A).split(','))[1]
            data2=map(float,rexp.sub('', resp_B).split(','))[1]
            ydata["1"].append(data1)
            ydata["2"].append(data2)
        
            thread2.on_running(xdata, ydata)
            print sys._current_frames()
            next_call = next_call+1  #timer=1s

    
    
    
        

class plotdata(Thread):
    def __init__(self):
        super(plotdata, self).__init__()
        self.running = True
#         self.q = Queue.LifoQueue()
#         self.l=deque()
#         global l
        

        
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
        self.figure, self.axarr = plt.subplots(2,sharex=True)
        self.lines1, = self.axarr[0].plot([],[])
        #Autoscale on unknown axis and known lims on the other
        self.axarr[0].set_autoscaley_on(True)
        self.axarr[0].set_xlim(0, 200)
        self.lines2, = self.axarr[1].plot([],[])
        self.axarr[0].grid()
        self.axarr[1].grid()

    def on_running(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines1.set_xdata(xdata["1"])
        self.lines1.set_ydata(ydata["1"])
        self.lines2.set_ydata(ydata["2"])
        self.lines2.set_xdata(xdata["2"])
        #Need both of these in order to rescale
        self.axarr[0].relim()
        self.axarr[1].relim()
        self.axarr[0].autoscale_view()
        self.axarr[1].autoscale_view()
        
        #We need to draw *and* flush
        self.figure.canvas.draw()
 
        self.figure.canvas.flush_events()
  

    
#     def run(self):
#         q = self.l 
#         try:
#             # block for 1 second only:
#             if len(q)==0:
#                 print "list is empty!!"
#             else:  
#                 value=q[len(q)-1] #always process latest data in list
#                 if value["cmd"] == "show" :
#                     stock= value["sym"]
# #                     starttime=float(value["start"])
# #                     stoptime=float(value["end"])
#                     interval=int(value["interval"])
# #                     ticknum=int((stoptime-starttime)/interval)
#                     print "#stock is:",stock
#                     to_str_show={"request":{"command":"subscribe", "client": "viewer","symlist":["QQQ","SPY"]}}
#                     to_streamer_update={"request":{"command":"update","client":"viewer","interval":"%ss"%interval,"mask":"0111111b","symlist":["QQQ","SPY"]}}
#                     input_show=dumps(to_str_show)+"\n"
#                     input_update=dumps(to_streamer_update)+"\n"
#                 a1 = deque([0]*100)
# 
#                 print "begin connect to streamer"
# #                 i=1  
#                 for x in [1]:  # pull and plot the data every second, this is only for real time simulated data
#                     s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # as client for simu     
# #                     s.connect(("192.168.1.121",8091))
#                     s.connect(("localhost",8091))
#                     print "connected to streamer!"
#                     print "%sth time: send subscribe request to streamer:" %x,input_show
#                     s.send(input_show)
#                     sleep(1)
#                     print "send out to streamer."
# 
#                     sleep(0.5)
# 
#                     self.on_launch()
#                     xdata = {"1":[],"2":[]}
#                     ydata = {"1":[],"2":[]}
#                     for x in  np.arange(0,2000,1):
#                         sleep(0.1)
#                         s.send(input_update)
#                         print "have sent update command to streamer.."
# #                         print "recv data1 from streamer.."
#                         resp1 = s.recv(1024*10)
# #                         print "received simu's data1:",resp1
#                         print "received data from streamer!!"
#                         xdata["1"].append(x)
#                         xdata["2"].append(x)
#                         print resp1,"dd"
#                         resp_A=resp1.split('\n')[0]
#                         resp_B=resp1.split('\n')[1]
#                         
#                         rexp = re.compile(r'[^\d.,]+')
#                         data1=map(float,rexp.sub('', resp_A).split(','))[1]
#                         data2=map(float,rexp.sub('', resp_B).split(','))[1]
#                         ydata["1"].append(data1)
#                         ydata["2"].append(data2)
# 
#                         self.on_running(xdata, ydata)
#                         print sys._current_frames()
# #                     self.figure.close()
#                     
#                     
#         except len(q)==0:
#             sys.stdout.write('.')
#             sys.stdout.flush()
#         #
#         if  len(q)>100:
#             print "list length is %s, which is larger than 100, remove last one:" %len(q)
#             q.pop()
#             print list(q)

stopFlag =Event()
thread = recvdata(stopFlag)
thread2 = plotdata()
 
# stopFlag.set() 

class forController(rpyc.Service):
    def exposed_show(self,cmd):
        print "called by controller--- cmd_show"
        thread.start()
        thread.connect()    
        thread.streaming()
        
    def exposed_list(self,cmd):
        print "called by controller--- cmd_show"
        list=thread.list()
        return  list   






    
    
    
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

def main(): 
    t = ThreadedServer(forController, port = 8090)
    t.start()
     
#########################################################
 
if __name__ == "__main__":
    main()
