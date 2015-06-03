# viewer 2.0

import SocketServer
from json import loads,dumps 
import socket
import threading 
import time
#import sys
# import matplotlib.pyplot as plt
#import numpy as np
#import re
import dataAPI


q=[]               # q[{'cmd': {'type':'r','symbol':'QQQ',...}, 'data':{'time':[],'price':[],'vol':[],'ma':[[],[],..]}, 'dirty': True } , {}, ...]
RTDataReceiver={}      # this is the dictionary mapping interval to a thread of receiver
                        

# Cmd handler class, only one stance. 
class ViewerCmdHandler(SocketServer.BaseRequestHandler):

    ##  override the handle() method to implement communication to the client
    def handle(self): 
        global q
        print 'handler started..'
        cmd_type,ID, pos, interval, params = self.parseCmd() 	#parseCmd recev/parse cmd from controller
        print cmd_type,ID, pos, interval, params
        if cmd_type == 'del':
            delSymbol=q[ID]['cmd']['symbol']
            delSymType=q[ID]['cmd']['type']
                
            if delSymType=='r': 
                RTDataReceiver(interval).unsubscribeRealtime(delSymbol)
                
            elif delSymType=='h': 
                delStarTime=q[ID]['cmd']['start']
                delStopTime=q[ID]['cmd']['end']
                RTDataReceiver(interval).unsubscribeHistory([delSymbol,delStarTime,delStopTime])     #For history data, this api should not have real effect
            else:
                print "unvalid symbol type!!"			    
            
            self.delfromQueue(ID)
            
        elif cmd_type == 'mv':
            self.mvInQueue(ID, pos)
              
        elif cmd_type == 'list':
            self.listQueue()
            
        elif cmd_type == 'add':
            # need make sure no add duplicate item
            existing=0
            if q!=[]:                   # need consider the case of q=[] 
                for q1 in q:            # check if there is any same item in q already            
                    barTyp=q1['cmd']['price']       # get bar type from item in q
                    maTyp= q1['cmd']['movingave']   # get ma type from item in q, maTyp is a list
                    # realtime case check:
                    if (q1['cmd']['interval']==interval) and  (q1['cmd']['symbol']==params['symbol']) and (barTyp == params['price']) and (maTyp == params['movingave']) and (q1['cmd']['type']==params['type']) and (params['type'] == 'r'):
                        print 'already has same realtime item in q!'
                        existing=1
                        break
                    # history case check:
                    if  params['type'] == 'h':
                        if (q1['cmd']['interval']==interval) and  (q1['cmd']['symbol']==params['symbol']) and (barTyp == params['price']) and (maTyp == params['movingave']) and (q1['cmd']['type']==params['type'])  and (q1['cmd']['start']==params['start']) and (q1['cmd']['end']==params['end']):
                            print 'already has same realtime item in q!'
                            existing=1
                            break
            
            if existing==0 :          
                self.addtoQueue(params,pos)
                                                    
                if (params['type'] == 'h'):
                    #history data, no need request data frequtly based on interver  
                    histRcver = DataReceiver('Viewer_history_'+params['symbol'],params)     # clientName,params
                    histRcver.subscribeHistory([params['symbol'],params['start'],params['end']]) 
                    histRcver.start()                                  
                
                else:         #real time data	    	
                    
                    # if it's new interval  
                    if(RTDataReceiver[interval]) == None:                              
                        RTDataReceiver[interval] =  DataReceiver('Viewer_real_'+interval,params)  
                        RTDataReceiver[interval].subscribeRealtime(params['symbol'])
                        RTDataReceiver[interval].start()
                    
                    else:      # if it's existing  interval                        
                        symbolPool=[i['cmd']['symbol'] for i in q ] 
                        if params['symbol'] in symbolPool:     # if it's a existing symbol 
                            price,ma,vol=self.findCommonPriceMA(self,interval,params['symbol'])
                            RTDataReceiver(interval).updatePriceMAtype(price,ma,vol)   	    
                   
                        else:             # if it's a new symbol		     
                            price,ma,vol=self.findCommonPriceMA(self,interval,params['symbol'])
                            RTDataReceiver(interval).subscribeRealtime(params['symbol'])			         
        
        else:
            pass


    def findCommonPriceMA(self,interval,symbol):
        global q        
        price=[]                                   # issue: need change DataAPI's udpate API to receive price parameter as a list
        ma=[]
        vol='n'
        for i in q:
            if i['cmd']['interval']==interval and i['cmd']['type']=='r':   # only apply to realtime data
                price+=i['cmd']['price']
                ma+=i['cmd']['movingave']
                if i['cmd']['volume']=='y':
                    vol='y' 
             
        price=list(set(price))
        ma=list(set(ma))        
        return price, ma, vol


    def parseCmd(self):
        params={'type':None,'symbol':None,'interval':None,'start':None,'end':None,'price':None,'volume':None,'movingave':None}
        #cmd={}
        cmd=loads(self.request.recv(10*1024).strip())     # self.request is the TCP socket connected to the client	    
        
        print 'parseCmd started..'
        print cmd  
        cmd_type=cmd['cmd']
        
        if cmd_type=='add':
            ID=0
            pos=cmd['pos']
            interval=cmd['interval']
            # real or histor
            for i in ['type','symbol','interval','price','volume','movingave']:
                params[i]= cmd[i]
                                    
            if cmd['type']=='h':      # only historical
                params['start']=cmd['start']
                params['end']=cmd['end']    
                                                        # params{'type':'r', 'symbol':'QQQ','interval':'1m','start':'20150225-102359','end':'20150225-123459','price':['o','h','c'],'volume':'y','movingave':['10m','1h']}            
        elif cmd_type=='mv' or cmd_type=='del':
            ID= self.cmd['id']
            pos=cmd['pos']
            interval=None
        
        elif cmd_type=='list':
            ID=None; pos=None; interval=None
        else: 
            print 'Not valid cmd type!' 
                
        return cmd_type,ID,pos,interval,params


    def delfromQueue(self,ID):
        global q
        del q[ID]
    
    def mvInQueue(self,ID,pos):       
        global q
        q.insert(pos,q.pop(ID)) 
    
    def addtoQueue(self,params,pos):
        global q
        newItem={}
        newItem['cmd']= params     
        newItem['data']= {'time':[],'price':[],'vol':[],'ma':[]}
        newItem['dirty']=False
        q.insert(pos,newItem)

    def listQueue(self):
        global q
        i=1
        for p in q: 
            print i, p['cmd']['symbol'],p['cmd']['type'] 
            i+=1  
    
        
# DataReceiver class, multiple instances
class DataReceiver(threading.Thread):
    def __init__(self, client,params):    
        super(DataReceiver, self).__init__()
        self.running = True
        
        self.dataapi=  dataAPI.DataAPI(client)	 
        self.interval=params['interval']
        self.dataType=params['type']
        self.priceType=params['price']
        self.maType=params['movingave']
        self.volType=params['volume']       
        self.data={}
    
    def updatePriceMAtype(self, price,ma,vol):       #wrapper to update price/ma type inside instance
        self.priceType=price
        self.maType=ma
        self.volType=vol
        
        
    def ConvertInterval(self, interval):              # issue: should we write this as seperate lib?
        ConvTable={"1s":1, "5s":5 ,"10s":10, "30s":30, "1m":60, "5m":300, "10m":600, "30m":1800, "1h":3600}
        return ConvTable[interval]
    
    def subscribeRealtime(self, sym):
        self.dataapi.subscribeRealtime(sym)    
         
    def subscribeHistory(self, symPeriodList):
        self.dataapi.subscribeRealtime(symPeriodList)  
    
    def unsubscribeRealtime(self, sym):
        self.dataapi.unsubscribeRealtime(sym)
        
    def unsubscribeHistory(self, symPeriodList):
        self.dataapi.unsubscribeHistory(symPeriodList)
        
    def run(self):
        global q      
        if  self.dataType=='h':            
            while 1:
                data = loads(self.dataapi.update(self.interval,self.priceType,self.maType))    # issue:dataAPI update() do not have volume parameter?
                if data is not None:
                    self.fillDataQueue(q, data)     #q[id][data]= {'time':[],'price':[],'vol':[],'ma':[[],[],..]}
                else:
                    break                               # issue: assuem DataAPI will give None if in end, not in the middle.
                                       
        elif self.dataType=='r':
            previousTimeStmp=''
            next_call = time.time() 
#             while not self.stopped.wait(next_call - time.time()):  #timer compensate   
            while not time.sleep(next_call - time.time()):         
                print "##Debug: price type is %s" %self.priceType                
                data = loads(self.dataapi.update(self.interval,self.priceType,self.maType))                
                print data
                if data is not None:
                    while data['timestamp']==previousTimeStmp :          # re-send update() if timestamp no change
#                     if 0:
                        print 'detected same timestamp, re-send request...'
                        data = loads(self.dataapi.update(self.interval,self.priceType,self.maType))
                    
                    self.fillDataQueue(q, data)     #q[id][data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[[20:1700, 19.8:1800],[19.8:1600, 19.9:1600],..]}                   
                    print '##for debug: q now is:', q
                    previousTimeStmp=data['timestamp']
                next_call = next_call+ self.ConvertInterval(self.interval)
                
        else:
            print 'Not valid data_type!'


    def fillDataQueue(self, QData,RevData):      #q[id][data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[['20:1700', '19.8:1800'],['19.8:1600', '19.9:1600'],..]}
            global q      # we need change global q in this function
            xdata=RevData['timestamp']     
            
            for symData in RevData['data']:            # DataAPI should return bar data like:   'bar': {'h':200,'vol':20000}  .
                sym=symData['symbol']
                bar=symData['bar'].keys()           # get bar data type from received data, it's a list
                ma=set(symData['ma'].keys())                # get bar data type from received data, it's a set
                delay=symData['delay']                 # issue: what we use delay for?
                
                for q1 in q:                 # note: there could be multiple item in q be feed data from current symData, like differnt price/ma type
                    barTyp=q1['cmd']['price']       # get bar type from item in q
                    maTyp= set(q1['cmd']['movingave'])   # get ma type from item in q, maTyp is a set
                    print barTyp, maTyp
                    print 'loop check to items in q, now is:', q1
                    #print "####### current thread params:",self.interval,sym,bar,ma,self.dataType 
                    if (q1['cmd']['interval']==self.interval) and  (q1['cmd']['symbol']==sym) and (barTyp in bar) and (q1['cmd']['type']==self.dataType) and (maTyp.issubset(ma)):
                        print 'found matched item in q'
                        idx=q.index(q1)
                        q[idx]['data']['time'].append(xdata)
                        q[idx]['data']['price'].append(symData['bar'][barTyp])
                        q[idx]['data']['vol'].append(symData['bar']['vol'])
                        
                        tempMA=[]
                        for i in maTyp:           # in order of ma type in q1
                            tempMA.append(symData['ma'][i])   # return ma value:vol pair, after append,  data looks like:['20:1700', '19.8:1800']                      
                        
                        q[idx]['data']['ma'].append(tempMA)        
                        q[idx]['dirty'] = True
        
    
## to-do: finish the implement of plot block
     
# dataplotter class, single instance
class DataPlotter(threading.Thread):
    def __init__(self):       
        super(DataPlotter, self).__init__()
        self.running = True
        
        #Set up # of subplots
        self.figure, self.axarr = plt.subplots(2,sharex=True)       # to-do: extend to 6 subplots
        
        #Set up 1st plot
        self.lines11, = self.axarr[0].plot([],[])   # price
        self.lines12, = self.axarr[0].plot([],[])   # vol
        self.lines13, = self.axarr[0].plot([],[])   # ma1
        self.lines14, = self.axarr[0].plot([],[])   # ma1_vol
        self.lines15, = self.axarr[0].plot([],[])   # ma2
        self.lines16, = self.axarr[0].plot([],[])   # ma2_vol     # to-do: add more ma type
        self.axarr[0].set_autoscaley_on(True)    # auto-scale on y
        self.axarr[0].set_xlim(0, 1000)         # to-do: for realtime: scale xlim based on interval; for history: auto scale
        
        #Set up 2nd plot 
        self.lines21, = self.axarr[1].plot([],[])   # price
        self.lines22, = self.axarr[1].plot([],[])   # vol
        self.lines23, = self.axarr[1].plot([],[])   # ma1
        self.lines24, = self.axarr[1].plot([],[])   # ma1_vol
        self.lines25, = self.axarr[1].plot([],[])   # ma2
        self.lines26, = self.axarr[1].plot([],[])   # ma2_vol
        self.axarr[1].set_autoscaley_on(True)    # auto-scale on y
        self.axarr[1].set_xlim(0, 1000)  
        
        self.axarr[0].grid()        # add grid
        self.axarr[1].grid()
        
    def run(self):
        global q
        next_call = time.time() 
        while not time.sleep(next_call - time.time()):  #timer  
            #for qi in q[0:2]:
                #if qi[dirty] = True:            
            self.plotData(q[0:2])
        next_call = next_call+ 1              # plot all subplots every 1s
                
                
    def plotData(self,data):
        global q                      #q[id][data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[['20:1700', '19.8:1800'],['19.8:1600', '19.9:1600'],..]}
        #Update plot data
        self.lines11.set_xdata(data[0]['data']["time"])      # to-do: convert string timestamp to plot-able int
        self.lines11.set_ydata(data[0]['data']["price"])        
        self.lines12.set_xdata(data[0]['data']["time"])
        self.lines12.set_ydata([0]['data']["vol"])
        self.lines13.set_xdata(data[0]['data']["time"])         # to-do: auto select ma type based on data
        self.lines13.set_ydata([i[0].split(':')[0] for i in data[0]['data']["ma"] ])   # ma1 value
        self.lines14.set_xdata(data[0]['data']["time"])
        self.lines14.set_ydata([i[0].split(':')[1] for i in data[0]['data']["ma"] ])   # ma1 vol
        self.lines15.set_xdata(data[0]['data']["time"])
        self.lines15.set_ydata([i[1].split(':')[0] for i in data[0]['data']["ma"] ])   # ma2 value
        self.lines16.set_xdata(data[0]['data']["time"])
        self.lines16.set_ydata([i[1].split(':')[1] for i in data[0]['data']["ma"] ])   # ma2 vol
        
        #Update 2nd subplot data
        self.lines21.set_xdata(data[1]['data']["time"])      
        self.lines21.set_ydata(data[1]['data']["price"])        
        self.lines22.set_xdata(data[1]['data']["time"])
        self.lines22.set_ydata(data[1]['data']["vol"])
        self.lines23.set_xdata(data[1]['data']["time"])        
        self.lines23.set_ydata([i[0].split(':')[0] for i in data[1]['data']["ma"] ])   # ma1 value
        self.lines24.set_xdata(data[1]['data']["time"])
        self.lines24.set_ydata([i[0].split(':')[1] for i in data[1]['data']["ma"] ])   # ma1 vol
        self.lines25.set_xdata(data[1]['data']["time"])
        self.lines25.set_ydata([i[1].split(':')[0] for i in data[1]['data']["ma"] ])   # ma2 value
        self.lines26.set_xdata(data[1]['data']["time"])
        self.lines26.set_ydata([i[1].split(':')[1] for i in data[1]['data']["ma"] ])   # ma2 vol
           
                   
        #auto rescale
        self.axarr[0].relim()
        self.axarr[1].relim()
        self.axarr[0].autoscale_view()
        self.axarr[1].autoscale_view()
        
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
    



if __name__ == "__main__":

    # init the dict mapping interval to thread of receiver.
    RTDataReceiver={"1s":None,"5s":None, "10s":None, "30s":None, "1m":None, "5m":None, "10m":None, "30m":None, "1h":None} 
    
    #start a plotData thread. 
#     plot = DataPlotter()
#     plot.start()

    server = SocketServer.TCPServer(('localhost', 8090), ViewerCmdHandler)
    server.serve_forever()


    
