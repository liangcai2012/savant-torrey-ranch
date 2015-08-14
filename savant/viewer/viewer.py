# viewer 2.0

import SocketServer
from json import loads, dumps 
import socket
import threading 
import time
# import sys
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
plt.ion()
from matplotlib.finance import *
import matplotlib.dates as md
from matplotlib import gridspec

import numpy as np
# import re
import dataAPI
import datetime
import itertools

q = []  # q[{'cmd': {'type':'r','symbol':'QQQ',...}, 'data':{'time':[],'price':[],'vol':[],'ma':[[],[],..]}, 'dirty': True } , {}, ...]
RTDataReceiver = {}  # this is the dictionary mapping interval to a thread of receiver
                        

# Cmd handler class, only one stance. 
class ViewerCmdHandler(SocketServer.BaseRequestHandler):

    # #  override the handle() method to implement communication to the client
    def handle(self): 
        global q
        print '\n #####################debug:handler started..'
        while True:    
            temp = self.request.recv(10 * 1024).strip()  # loop to keep receiving   # self.request is the TCP socket connected to the client            
            if not temp:  # in case if server didn't received any valid cmd
                continue
            else:
                cmd = loads(temp)  # load() must deal with Json object, can not handle if temp=None or ''            
            cmd_type, ID, pos, interval, params = self.parseCmd(cmd)  # parseCmd recev/parse cmd from controller            
            print '\n #####################debug:received cmd is:', cmd_type, ID, pos, interval, params
            
            if cmd_type == 'del':
                delSymbol = q[ID]['cmd']['symbol']
                delSymType = q[ID]['cmd']['type']
                delInterval = q[ID]['cmd']['interval']
                print '\n #####################debug: del symbol is:', delSymbol
                
                if delSymType == 'r': 
                    RTDataReceiver[delInterval].unsubscribeRealtime(delSymbol)  # need use 'delInterval' here instead of 'interval', the later one is None    
                elif delSymType == 'h': 
                    delStarTime = q[ID]['cmd']['start']
                    delStopTime = q[ID]['cmd']['end']
                    RTDataReceiver[delInterval].unsubscribeHistory([delSymbol, delStarTime, delStopTime])  # For history data, this api should not have real effect                           
                else:
                    print "unvalid symbol type!!"                           
                
                self.delfromQueue(ID)
                # need reset followed subplots xlim
                for i in range(ID, min(2, len(q))):  # note: need reset all followed subplot's xlim, and need check each one if real/history!!
                        if q[i]['cmd']['type'] == 'r':
                            plot.reset_xlim_real(i, False)
                        elif q[i]['cmd']['type'] == 'h': 
                            plot.reset_xlim_history(i) 
                        else:
                            print 'there are invalid data type!!'
                            
            elif cmd_type == 'mv':
                self.mvInQueue(ID, pos)
                typeNew = q[pos]['cmd']['type']
                typeOld = q[ID]['cmd']['type']
                if typeNew == 'r':
                    plot.reset_xlim_real(pos, False) 
                    print 'reset realtime xlim for mv command!!!!!!!!!!'
                elif typeNew == 'h':
                    plot.reset_xlim_history(pos)
                    print 'reset history xlim for mv command!!!!!!!!!!'
                else:
                    print 'no valid type for target item'     
                
                if typeOld == 'r':
                    plot.reset_xlim_real(ID, False) 
                elif typeOld == 'h':
                    plot.reset_xlim_history(ID)
                else:
                    print 'no valid type for source item' 
                    
                
            elif cmd_type == 'list':
                self.listQueue()
            
            elif cmd_type == 'add':
            # need make sure no add duplicate item
                existing = 0
                if q != []:  # need consider the case of q=[] 
                    for q1 in q:  # check if there is any same item in q already            
                        barTyp = q1['cmd']['price']  # get bar type from item in q
                        maTyp = q1['cmd']['movingave']  # get ma type from item in q, maTyp is a list
                        # realtime case check:
                        if (q1['cmd']['interval'] == interval) and  (q1['cmd']['symbol'] == params['symbol']) and (barTyp == params['price']) and (maTyp == params['movingave']) and (q1['cmd']['type'] == params['type']) and (params['type'] == 'r'):
                            print 'already has same realtime item in q!'
                            existing = 1
                            break
                        # history case check:
                        if  params['type'] == 'h':
                            if (q1['cmd']['interval'] == interval) and  (q1['cmd']['symbol'] == params['symbol']) and (barTyp == params['price']) and (maTyp == params['movingave']) and (q1['cmd']['type'] == params['type'])  and (q1['cmd']['start'] == params['start']) and (q1['cmd']['end'] == params['end']):
                                print 'already has same realtime item in q!'
                                existing = 1
                                break
            
                if existing == 0 :          
                    self.addtoQueue(params, pos)  # after addtoQueue, now at least we have ['cmd'] data  in current item, this info will used to guide reset_subplot
                                                    
                    if (params['type'] == 'h'):
                        # history data, no need request data frequtly based on interver  
                        histRcver = DataReceiver('Viewer_history_' + params['symbol'], params)  # clientName,params
                        histRcver.subscribeHistory([params['symbol'], params['start'], params['end']]) 
                        histRcver.start()    
#                         plot.reset_xlim_history(pos)      # no need set here, will be setup in plot loop                      
                
                    elif(params['type'] == 'r'):  # real time data            
                    
                        # if it's new interval  
                        if(RTDataReceiver[interval]) == None:                              
                            print '\n ######### create new thread for new interval group....'
                            RTDataReceiver[interval] = DataReceiver('Viewer_real_' + interval, params)  
                            RTDataReceiver[interval].subscribeRealtime(params['symbol'])
                            RTDataReceiver[interval].start()  
                        else:  # if it's existing  interval                        
                            symbolPool = [i['cmd']['symbol'] for i in q ] 
#                             print'\n#####################debug: symbolPool is:',symbolPool
#                             print'\n#####################debug: current symbol and interval  is:',params['symbol'],interval
                            if params['symbol'] in symbolPool:  # if it's a existing symbol 
                                price, ma, vol = self.findCommonPriceMA(interval, params['symbol'])
                                print '\n #####################debug: add a existing symbol, but different price/MA type###########'
#                                 print '#####################debug: udpated price/MA is:',price,ma
                                RTDataReceiver[interval].updatePriceMAtype(price, ma, vol)           
                            else:  # if it's a new symbol             
                                price, ma, vol = self.findCommonPriceMA(interval, params['symbol'])
                                RTDataReceiver[interval].subscribeRealtime(params['symbol'])                     
                            # reset xlim of new added plot    
                        plot.reset_xlim_real(pos, True)  # NOTE:need reset the xlim, unless there will be 'blank' in previous x 
                    else:
                        print 'not valid data type!!'
                        
                    # reset xlim of all followd plots
                    for i in range(pos + 1, min(6, len(q))):  # note: need reset all followed subplot's xlim, and need check each one if real/history!!
                        if q[i]['cmd']['type'] == 'r':
                            plot.reset_xlim_real(i, False)
                        elif q[i]['cmd']['type'] == 'h': 
                            plot.reset_xlim_history(i) 
                        else:
                            print 'there are invalid data type!!'      
            else:
                pass


    def findCommonPriceMA(self, interval, symbol):  # params{'type':'r', 'symbol':'QQQ','interval':'1m','start':'20150225-102359','end':'20150225-123459','price':['o','h','c'],'volume':'y','movingave':['10m','1h']} 
        global q        
        price = []  # issue: need change DataAPI's udpate API to receive price parameter as a list
        ma = []
        vol = 'n'
        for i in q:
            if i['cmd']['interval'] == interval and i['cmd']['type'] == 'r':  # only apply to realtime data
                price += i['cmd']['price']
                ma += i['cmd']['movingave']
                if i['cmd']['volume'] == 'y':
                    vol = 'y' 
                    
        price = list(set(price))
        ma = list(set(ma))        
        return price, ma, vol


    def parseCmd(self, cmd):
        params = {'type':None, 'symbol':None, 'interval':None, 'start':None, 'end':None, 'price':None, 'volume':None, 'movingave':None}
        # cmd={}
#         cmd=loads(self.request.recv(10*1024).strip())     # self.request is the TCP socket connected to the client        
#         self.request.close()
        print '\n #####################debug:parseCmd started..'
        print cmd  
        cmd_type = cmd['cmd']
        
        if cmd_type == 'add':
            ID = 0
            pos = cmd['pos']
            interval = cmd['interval']
            # real or histor
            for i in ['type', 'symbol', 'interval', 'price', 'volume', 'movingave']:
                params[i] = cmd[i]
                                    
            if cmd['type'] == 'h':  # only historical
                params['start'] = cmd['start']
                params['end'] = cmd['end']    
                                                        # params{'type':'r', 'symbol':'QQQ','interval':'1m','start':'20150225-102359','end':'20150225-123459','price':['o','h','c'],'volume':'y','movingave':['10m','1h']}            
        elif cmd_type == 'mv' or cmd_type == 'del':
            ID = cmd['id']
            pos = cmd['pos']
            interval = None
        
        elif cmd_type == 'list':
            ID = None; pos = None; interval = None
        else: 
            print 'Not valid cmd type!'     
        return cmd_type, ID, pos, interval, params


    def delfromQueue(self, ID):
        global q
        if len(q)>0:
            del q[ID]
        else:
            print 'q is already empty, can not del anymore!!!'
    
    def mvInQueue(self, ID, pos):       
        global q
        q.insert(pos, q.pop(ID)) 
    
    def addtoQueue(self, params, pos):
        global q
        newItem = {}
        newItem['cmd'] = params     
        newItem['data'] = {'time':[], 'price':[], 'vol':[], 'ma':[]}
        newItem['dirty'] = False
        q.insert(pos, newItem)

    def listQueue(self):
        global q
        i = 1
        if len(q) ==0:
            print "q is empty now!"
        else:
            for p in q: 
                print '\n##', i, p['cmd']['symbol'], p['cmd']['type'], p['cmd']['price'], p['cmd']['movingave'], p['cmd']['interval'],
                i += 1  


# global func    
def ConvertInterval(interval):              
    ConvTable = {"1s":1, "5s":5 , "10s":10, "30s":30, "1m":60, "5m":300, "10m":600, "30m":1800, "1h":3600}
    return ConvTable[interval] 
      
def ConvertMA(idx, isInt):             
    ConvTable1 = {0:'1s', 1:"5s" , 2:"10s", 3:"30s", 4:"1m", 5:"5m", 6:"10m", 7:"30m", 8:"1h"}
    ConvTable2 = {"1s":0, "5s":1, "10s":2, "30s":3, "1m":4, "5m":5, "10m":6, "30m":7, "1h":8}
    MA = []
#     print 'idx is:',idx
    if isInt == True:
        for i in idx:
            MA.append(ConvTable1[i])
    else:
        return ConvTable2[idx]
        
    return MA       

 
# DataReceiver class, multiple instances
class DataReceiver(threading.Thread):
    def __init__(self, client, params):    
        super(DataReceiver, self).__init__()
        self.running = True
        
        self.dataapi = dataAPI.DataAPI(client)     
        self.interval = params['interval']
        self.dataType = params['type']
        self.priceType = params['price']
        self.maType = params['movingave']
        self.volType = params['volume']       
        self.data = {}
    
    def updatePriceMAtype(self, price, ma, vol):  # wrapper to update price/ma type inside instance
        self.priceType = price
        self.maType = ma
        self.volType = vol
    
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
        
        if  self.dataType == 'h':            
            i = 0
            while i < 6200:  # just for debugging
                i = i + 1
                time.sleep(0.01)  # temp for debugging
                data = loads(self.dataapi.update(self.interval, self.priceType, self.maType))  # issue:dataAPI update() do not have volume parameter?
                if data is not None:
                    self.fillDataQueue(q, data)  # q[id][data]= {'time':[],'price':[],'vol':[],'ma':[[],[],..]}
                else:
                    break  # issue: assuem DataAPI will give None if in end, not in the middle.
                                       
        elif self.dataType == 'r':
            previousTimeStmp = ''
            next_call = time.time() 
#             while not self.stopped.wait(next_call - time.time()):  #timer compensate   
            while not time.sleep(next_call - time.time()):         
#                 print "##Debug: price type is %s" %self.priceType
                t1=time.time()                
                data = loads(self.dataapi.update(self.interval, self.priceType, self.maType))                
#                 print data
                if data is not None:
#                     while data['timestamp']==previousTimeStmp :          # re-send update() if timestamp no change
                    if 0:  # temp for debugging  only
                        print '\n detected same timestamp, re-send request...'
                        data = loads(self.dataapi.update(self.interval, self.priceType, self.maType))
                    
                    self.fillDataQueue(q, data)  # q[id][data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[[20:1700, 19.8:1800],[19.8:1600, 19.9:1600],..]}                   
#                     print '\n ##for debug: q now is:', q
                    previousTimeStmp = data['timestamp']
                t2=time.time()
#                 print 'recv data colaps time:' ,t2-t1
                next_call = next_call + ConvertInterval(self.interval)
        else:
            print '\n Not valid data_type or history data ALL received!'


    def fillDataQueue(self, QData, RevData):  # q[id][data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[['20:1700', '19.8:1800'],['19.8:1600', '19.9:1600'],..]}
            global q  # we need change global q in this function
            xdata = RevData['timestamp']     
            
            for symData in RevData['data']:  # DataAPI should return bar data like:   'bar': {'h':200,'vol':20000}  .
                sym = symData['symbol']
                bar = symData['bar'].keys()  # get bar data type from received data, it's a list
#                 ma=set(symData['ma'].keys())                # get bar data type from received data, it's a set,because it's easy to use issubset()
                ma = set(ConvertMA([i for i, j in enumerate(symData['ma']) if j is not None], True))
                delay = symData['delay']  # issue: what we use delay for?
                
                for q1 in q:  # note: there could be multiple item in q be feed data from current symData, like differnt price/ma type
                    barTyp = q1['cmd']['price']  # get bar type from item in q
                    maTyp = set(q1['cmd']['movingave'])  # get ma type from item in q, maTyp is a set
#                     print 'barTyp and maTyp are:', barTyp, maTyp
#                     print 'loop check to items in q, now is:', q1
                    # print "####### current thread params:",self.interval,sym,bar,ma,self.dataType 
                    if (q1['cmd']['interval'] == self.interval) and  (q1['cmd']['symbol'] == sym) and (barTyp in bar) and (q1['cmd']['type'] == self.dataType) and (maTyp.issubset(ma)):
#                         print '\n found matched item in q'
                        idx = q.index(q1)
#                         print '###data[time] size is:',len(q[idx]['data']['time'])
                        if q[idx]['cmd']['type'] == 'r' and len(q[idx]['data']['time']) > 100:  # for realtime data, only keep fix length data,when filled, cut first half part
                            print '*******for debug: current item length exceed limit, cut first half then refill.....'
                            del q[idx]['data']['time'][0:50]
                            del q[idx]['data']['price'][0:50]
                            del q[idx]['data']['vol'][0:50]
                            del q[idx]['data']['ma'][0:50]
                            # reset the xlim after 'cut'
#                             if idx == 0:
                            plot.reset_xlim_real(idx, False)
#                             if idx == 1:
#                                 plot.reset_xlim_real(1, False)
                        
                        q[idx]['data']['time'].append(xdata)
                        q[idx]['data']['price'].append(symData['bar'][barTyp])
                        q[idx]['data']['vol'].append(symData['bar']['vol'])
                        
                        tempMA = []
#                         tempMA={}
#                         print symData['ma']
                        for i in maTyp:  # in order of ma type in q1
#                             tempMA.append(symData['ma'][i]) 
                            tempMA.append(symData['ma'][ConvertMA(i, False)])  # return ma value:vol pair, after append,  data looks like:['20:1700', '19.8:1800']                      
                        
                        q[idx]['data']['ma'].append(tempMA)  # q[id][data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[[20:1700, 19.8:1800],[19.8:1600, 19.9:1600],..]} 
                        q[idx]['dirty'] = True
        
    

# dataplotter class, single instance
# class DataPlotter(threading.Thread):
class DataPlotter():    
#     def __init__(self):
#         super(DataPlotter, self).__init__()
#         self.running = True

    def launch(self):          
        # Set up of subplots
#         self.figure, self.axarr = plt.subplots(4,3)       # to-do: extend to 6 subplots
        
        self.axarr = []
        self.figure = plt.figure() 
#         gs = gridspec.GridSpec(4, 3, width_ratios=[2, 1, 1], height_ratios=[4, 2, 2, 1])
#         for i in range(12):
#             self.axarr.append(plt.subplot(gs[i]))
#             self.axarr[i].grid()  # add grid to all subplots
        
        gs = gridspec.GridSpec(9,3)
        self.axarr.append(plt.subplot(gs[:4,:-1]))  #subplot1
        self.axarr.append(plt.subplot(gs[4:6,:-1])) 
        plt.setp( self.axarr[0].get_xticklabels(), visible=False)  # invisible vol suplot's x-axes
        
        self.axarr.append(plt.subplot(gs[:2,-1])) #subplot2
        self.axarr.append(plt.subplot(gs[2,-1]))
        plt.setp( self.axarr[2].get_xticklabels(), visible=False) 
        
        self.axarr.append(plt.subplot(gs[3:5,-1]))  #subplot3
        self.axarr.append(plt.subplot(gs[5,-1]))
        plt.setp( self.axarr[4].get_xticklabels(), visible=False) 
        
        self.axarr.append(plt.subplot(gs[6:8,0])) #subplot4
        self.axarr.append(plt.subplot(gs[-1,0]))
        plt.setp( self.axarr[6].get_xticklabels(), visible=False) 
        
        self.axarr.append(plt.subplot(gs[6:8,1])) #subplot5
        self.axarr.append(plt.subplot(gs[-1,1]))
        plt.setp( self.axarr[8].get_xticklabels(), visible=False) 
        
        self.axarr.append(plt.subplot(gs[6:8,2])) #subplot6
        self.axarr.append(plt.subplot(gs[-1,2]))
        plt.setp( self.axarr[10].get_xticklabels(), visible=False) 
        
     
        for i in self.axarr:
            i.grid()      # add grid to all subplots
        
        # Set up all 6 subplot's line
        self.lines=[]
        last_idx=0
        j=0
        marker = itertools.cycle(('b-', 'g-', 'c-', 'm-','y-','k-','co','mo','yo','ko')) 
        for i in range(10*6):
            if i/10>last_idx:    # for every 6 loops, axarr[] idx increase, for exampe: axarr[0],axarr[1] -> axarr[2],axarr[3] 
                print i,i/10+j+1,i/10+j+2
                self.lines.append(self.axarr[i/10+j+1].plot([], [], marker.next())[0])
                self.lines.append(self.axarr[i/10+j+2].plot([], [], marker.next())[0])
                j=j+1
            else:
                print i,i/10+j,i/10+j+1
                self.lines.append(self.axarr[i/10+j].plot([], [], marker.next())[0])
                self.lines.append(self.axarr[i/10+j+1].plot([], [], marker.next())[0])
            last_idx=i/10
        
#         self.lines11, = self.axarr[0].plot([], [], 'b-')  # price      
#         self.lines12, = self.axarr[1].plot([], [], 'r-')  # vol
#         self.lines13, = self.axarr[0].plot([], [], 'g-')  # ma1
#         self.lines14, = self.axarr[1].plot([], [], 'g-')  # ma1_vol
#         self.lines15, = self.axarr[0].plot([], [], 'c-')  # ma2
#         self.lines16, = self.axarr[1].plot([], [], 'c-')  # ma2_vol     
#         self.lines17, = self.axarr[0].plot([], [], 'm-')  # ma3
#         self.lines18, = self.axarr[1].plot([], [], 'm-')  # ma3_vol     
#         self.lines19, = self.axarr[0].plot([], [], 'y-')  # ma4
#         self.lines1a, = self.axarr[1].plot([], [], 'y-')  # ma4_vol     
#         self.lines1b, = self.axarr[0].plot([], [], 'k-')  # ma5
#         self.lines1c, = self.axarr[1].plot([], [], 'k-')  # ma5_vol     
#         self.lines1d, = self.axarr[0].plot([], [], 'co')  # ma6
#         self.lines1e, = self.axarr[1].plot([], [], 'co')  # ma6_vol
#         self.lines1f, = self.axarr[0].plot([], [], 'mo')  # ma7
#         self.lines1g, = self.axarr[1].plot([], [], 'mo')  # ma7_vol
#         self.lines1h, = self.axarr[0].plot([], [], 'yo')  # ma8
#         self.lines1i, = self.axarr[1].plot([], [], 'yo')  # ma8_vol
#         self.lines1j, = self.axarr[0].plot([], [], 'ko')  # ma9
#         self.lines1k, = self.axarr[1].plot([], [], 'ko')  # ma9_vol
# 
# #         self.axarr[0,0].set_autoscaley_on(True)    # auto-scale on y
# 
#         # Set up 2nd plot 
#         self.lines21, = self.axarr[2].plot([], [], 'b-')  # price
#         self.lines22, = self.axarr[3].plot([], [], 'r-')  # vol
#         self.lines23, = self.axarr[2].plot([], [], 'g-')  # ma1
#         self.lines24, = self.axarr[3].plot([], [], 'g-')  # ma1_vol
#         self.lines25, = self.axarr[2].plot([], [], 'c-')  # ma2
#         self.lines26, = self.axarr[3].plot([], [], 'c-')  # ma2_vol
#         self.lines27, = self.axarr[2].plot([], [], 'm-')  # ma3
#         self.lines28, = self.axarr[3].plot([], [], 'm-')  # ma3_vol
#         self.lines29, = self.axarr[2].plot([], [], 'y-')  # ma4
#         self.lines2a, = self.axarr[3].plot([], [], 'y-')  # ma4_vol
#         self.lines2b, = self.axarr[2].plot([], [], 'k-')  # ma5
#         self.lines2c, = self.axarr[3].plot([], [], 'k-')  # ma5_vol
#         self.lines2d, = self.axarr[2].plot([], [], 'co')  # ma6
#         self.lines2e, = self.axarr[3].plot([], [], 'co')  # ma6_vol
#         self.lines2f, = self.axarr[2].plot([], [], 'mo')  # ma7
#         self.lines2g, = self.axarr[3].plot([], [], 'mo')  # ma7_vol
#         self.lines2h, = self.axarr[2].plot([], [], 'yo')  # ma8
#         self.lines2i, = self.axarr[3].plot([], [], 'yo')  # ma8_vol
#         self.lines2j, = self.axarr[2].plot([], [], 'ko')  # ma9
#         self.lines2k, = self.axarr[3].plot([], [], 'ko')  # ma9_vol
#         
#         # Set up 3rd plot 
#         self.lines31, = self.axarr[4].plot([], [], 'b-')  # price
#         self.lines32, = self.axarr[5].plot([], [], 'r-')  # vol
#         self.lines33, = self.axarr[4].plot([], [], 'g-')  # ma1
#         self.lines34, = self.axarr[5].plot([], [], 'g-')  # ma1_vol
#         self.lines35, = self.axarr[4].plot([], [], 'c-')  # ma2
#         self.lines36, = self.axarr[5].plot([], [], 'c-')  # ma2_vol
#         self.lines37, = self.axarr[4].plot([], [], 'm-')  # ma3
#         self.lines38, = self.axarr[5].plot([], [], 'm-')  # ma3_vol
#         self.lines39, = self.axarr[4].plot([], [], 'y-')  # ma4
#         self.lines3a, = self.axarr[5].plot([], [], 'y-')  # ma4_vol
#         self.lines3b, = self.axarr[4].plot([], [], 'k-')  # ma5
#         self.lines3c, = self.axarr[5].plot([], [], 'k-')  # ma5_vol
#         self.lines3d, = self.axarr[4].plot([], [], 'co')  # ma6
#         self.lines3e, = self.axarr[5].plot([], [], 'co')  # ma6_vol
#         self.lines3f, = self.axarr[4].plot([], [], 'mo')  # ma7
#         self.lines3g, = self.axarr[5].plot([], [], 'mo')  # ma7_vol
#         self.lines3h, = self.axarr[4].plot([], [], 'yo')  # ma8
#         self.lines3i, = self.axarr[5].plot([], [], 'yo')  # ma8_vol
#         self.lines3j, = self.axarr[4].plot([], [], 'ko')  # ma9
#         self.lines3k, = self.axarr[5].plot([], [], 'ko')  # ma9_vol
#         
#         # Set up 4th plot 
#         self.lines41, = self.axarr[6].plot([], [], 'b-')  # price
#         self.lines42, = self.axarr[7].plot([], [], 'r-')  # vol
#         self.lines43, = self.axarr[6].plot([], [], 'g-')  # ma1
#         self.lines44, = self.axarr[7].plot([], [], 'g-')  # ma1_vol
#         self.lines45, = self.axarr[6].plot([], [], 'c-')  # ma2
#         self.lines46, = self.axarr[7].plot([], [], 'c-')  # ma2_vol
#         self.lines47, = self.axarr[6].plot([], [], 'm-')  # ma3
#         self.lines48, = self.axarr[7].plot([], [], 'm-')  # ma3_vol
#         self.lines49, = self.axarr[6].plot([], [], 'y-')  # ma4
#         self.lines4a, = self.axarr[7].plot([], [], 'y-')  # ma4_vol
#         self.lines4b, = self.axarr[6].plot([], [], 'k-')  # ma5
#         self.lines4c, = self.axarr[7].plot([], [], 'k-')  # ma5_vol
#         self.lines4d, = self.axarr[6].plot([], [], 'co')  # ma6
#         self.lines4e, = self.axarr[7].plot([], [], 'co')  # ma6_vol
#         self.lines4f, = self.axarr[6].plot([], [], 'mo')  # ma7
#         self.lines4g, = self.axarr[7].plot([], [], 'mo')  # ma7_vol
#         self.lines4h, = self.axarr[6].plot([], [], 'yo')  # ma8
#         self.lines4i, = self.axarr[7].plot([], [], 'yo')  # ma8_vol
#         self.lines4j, = self.axarr[6].plot([], [], 'ko')  # ma9
#         self.lines4k, = self.axarr[7].plot([], [], 'ko')  # ma9_vol
#         
#         # Set up 5th plot 
#         self.lines51, = self.axarr[8].plot([], [], 'b-')  # price
#         self.lines52, = self.axarr[9].plot([], [], 'r-')  # vol
#         self.lines53, = self.axarr[8].plot([], [], 'g-')  # ma1
#         self.lines54, = self.axarr[9].plot([], [], 'g-')  # ma1_vol
#         self.lines55, = self.axarr[8].plot([], [], 'c-')  # ma2
#         self.lines56, = self.axarr[9].plot([], [], 'c-')  # ma2_vol
#         self.lines57, = self.axarr[8].plot([], [], 'm-')  # ma3
#         self.lines58, = self.axarr[9].plot([], [], 'm-')  # ma3_vol
#         self.lines59, = self.axarr[8].plot([], [], 'y-')  # ma4
#         self.lines5a, = self.axarr[9].plot([], [], 'y-')  # ma4_vol
#         self.lines5b, = self.axarr[8].plot([], [], 'k-')  # ma5
#         self.lines5c, = self.axarr[9].plot([], [], 'k-')  # ma5_vol
#         self.lines5d, = self.axarr[8].plot([], [], 'co')  # ma6
#         self.lines5e, = self.axarr[9].plot([], [], 'co')  # ma6_vol
#         self.lines5f, = self.axarr[8].plot([], [], 'mo')  # ma7
#         self.lines5g, = self.axarr[9].plot([], [], 'mo')  # ma7_vol
#         self.lines5h, = self.axarr[8].plot([], [], 'yo')  # ma8
#         self.lines5i, = self.axarr[9].plot([], [], 'yo')  # ma8_vol
#         self.lines5j, = self.axarr[8].plot([], [], 'ko')  # ma9
#         self.lines5k, = self.axarr[9].plot([], [], 'ko')  # ma9_vol
#         
#         # Set up 6th plot 
#         self.lines61, = self.axarr[10].plot([], [], 'b-')  # price
#         self.lines62, = self.axarr[11].plot([], [], 'r-')  # vol
#         self.lines63, = self.axarr[10].plot([], [], 'g-')  # ma1
#         self.lines64, = self.axarr[11].plot([], [], 'g-')  # ma1_vol
#         self.lines65, = self.axarr[10].plot([], [], 'c-')  # ma2
#         self.lines66, = self.axarr[11].plot([], [], 'c-')  # ma2_vol
#         self.lines67, = self.axarr[10].plot([], [], 'm-')  # ma3
#         self.lines68, = self.axarr[11].plot([], [], 'm-')  # ma3_vol
#         self.lines69, = self.axarr[10].plot([], [], 'y-')  # ma4
#         self.lines6a, = self.axarr[11].plot([], [], 'y-')  # ma4_vol
#         self.lines6b, = self.axarr[10].plot([], [], 'k-')  # ma5
#         self.lines6c, = self.axarr[11].plot([], [], 'k-')  # ma5_vol
#         self.lines6d, = self.axarr[10].plot([], [], 'co')  # ma6
#         self.lines6e, = self.axarr[11].plot([], [], 'co')  # ma6_vol
#         self.lines6f, = self.axarr[10].plot([], [], 'mo')  # ma7
#         self.lines6g, = self.axarr[11].plot([], [], 'mo')  # ma7_vol
#         self.lines6h, = self.axarr[10].plot([], [], 'yo')  # ma8
#         self.lines6i, = self.axarr[11].plot([], [], 'yo')  # ma8_vol
#         self.lines6j, = self.axarr[10].plot([], [], 'ko')  # ma9
#         self.lines6k, = self.axarr[11].plot([], [], 'ko')  # ma9_vol
        
#         self.axarr[0,1].set_autoscaley_on(True)  
        for i in self.axarr:
            i.set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))) + 100)  # we need set correct xlim here! unless may not see plot cureve because incorrect x-scale

#         plt.tight_layout()
        

    def reset_xlim_real(self, subplot, new=True):  # to deal such case: when subplot change stock, reset this subplot's xlim
        if subplot == 0:  # always keep fix points ploting, not fix 'time', so we need mutiple by interval
            if new == True:  # if is called by 'add', means item may not have real 'data'
#                 print '####Ture!!'
                self.axarr[0].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time())), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[0]['cmd']['interval']))))  # we use 'int(time.time()' here,because there may still no real data yet in the new item
                self.axarr[1].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time())), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[0]['cmd']['interval']))))
            else:
                self.axarr[0].set_xlim(q[0]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[0]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[0]['cmd']['interval']))))   
                self.axarr[1].set_xlim(q[0]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[0]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[0]['cmd']['interval']))))
                
        elif subplot == 1:
            if new == True:  # if is called by 'add', means item may not have real 'data'
                self.axarr[2].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[1]['cmd']['interval']))))   
                self.axarr[3].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[1]['cmd']['interval']))))
            else:
                self.axarr[2].set_xlim(q[1]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[1]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[1]['cmd']['interval']))))   
                self.axarr[3].set_xlim(q[1]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[1]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[1]['cmd']['interval']))))
        
        elif subplot == 2:
            if new == True:  # if is called by 'add', means item may not have real 'data'
                self.axarr[4].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[2]['cmd']['interval']))))   
                self.axarr[5].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[2]['cmd']['interval']))))
            else:
                self.axarr[4].set_xlim(q[2]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[2]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[2]['cmd']['interval']))))   
                self.axarr[5].set_xlim(q[2]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[2]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[2]['cmd']['interval']))))
        elif subplot == 3:
            if new == True:  # if is called by 'add', means item may not have real 'data'
                self.axarr[6].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[3]['cmd']['interval']))))   
                self.axarr[7].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[3]['cmd']['interval']))))
            else:
                self.axarr[6].set_xlim(q[3]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[3]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[3]['cmd']['interval']))))   
                self.axarr[7].set_xlim(q[3]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[3]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[3]['cmd']['interval']))))
        
        elif subplot == 4:
            if new == True:  # if is called by 'add', means item may not have real 'data'
                self.axarr[8].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[4]['cmd']['interval']))))   
                self.axarr[9].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[4]['cmd']['interval']))))
            else:
                self.axarr[8].set_xlim(q[4]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[4]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[4]['cmd']['interval']))))   
                self.axarr[9].set_xlim(q[4]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[4]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[4]['cmd']['interval']))))
        
        elif subplot == 5:
            if new == True:  # if is called by 'add', means item may not have real 'data'
                self.axarr[10].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[5]['cmd']['interval']))))   
                self.axarr[11].set_xlim(matplotlib.dates.date2num(datetime.datetime.fromtimestamp((time.time()))), matplotlib.dates.date2num(datetime.datetime.fromtimestamp(time.time()) + 100 * datetime.timedelta(0, ConvertInterval(q[5]['cmd']['interval']))))
            else:
                self.axarr[10].set_xlim(q[5]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[5]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[5]['cmd']['interval']))))   
                self.axarr[11].set_xlim(q[5]['data']['time'][0], matplotlib.dates.date2num(matplotlib.dates.num2date(q[5]['data']['time'][0]) + 100 * datetime.timedelta(0, ConvertInterval(q[5]['cmd']['interval']))))
        
        else:
            print 'invalid subplot # !!!'  
            
    def reset_xlim_history(self, subplot):  # to deal such case: when subplot change stock, reset this subplot's xlim
        if subplot == 0:
            ### opt1 ###
#             self.axarr[0,0].set_xlim(md.date2num(q[0]['cmd']['start']),md.date2num(q[0]['cmd']['end']))   # NOTE: we use use q[0]['cmd']['start'] here, because ['cmd'] is always there even there is no 'data' yet
#             self.axarr[1,0].set_xlim(md.date2num(q[0]['cmd']['start']),md.date2num(q[0]['cmd']['end']))
            ## opt2 ###
            self.axarr[0].set_autoscalex_on(True)   
            self.axarr[1].set_autoscalex_on(True)
        elif subplot == 1:
            self.axarr[2].set_autoscalex_on(True)  
            self.axarr[3].set_autoscalex_on(True) 
        elif subplot == 2:
            self.axarr[4].set_autoscalex_on(True)  
            self.axarr[5].set_autoscalex_on(True) 
        elif subplot == 3:
            self.axarr[6].set_autoscalex_on(True)  
            self.axarr[7].set_autoscalex_on(True) 
        elif subplot == 4:
            self.axarr[8].set_autoscalex_on(True)  
            self.axarr[9].set_autoscalex_on(True) 
        elif subplot == 5:
            self.axarr[10].set_autoscalex_on(True)  
            self.axarr[11].set_autoscalex_on(True)     
        else:
            print 'invalid subplot # !!!'        
        
         
    def go(self):  
        global q
        print '#########init q is: ', q
        next_call = time.time() 
        while not time.sleep(next_call - time.time()):  # somehow need add +0.00001 to remove errno22 exception in Linux env. For Windows, we don't need add this          
#             print '^^^^^^^^^^^^'
            t1=time.time()
            if  len(q) != 0  :
#                 print "\n@@@@@@@@@@@@@@@@@ under plotting q is:", q
                self.plotData()
            t2=time.time()
            print "plot colaps time:",t2-t1
            next_call = next_call + 2  # some instable found if set to 1s plotting rate.  for 2s rate, it's ok.
                
                
    def plotData(self):
        global q  # q[id][data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[['20:1700', '19.8:1800'],['19.8:1600', '19.9:1600'],..]}
        
        # Update 1st subplot data 
        
        for k in range(6):
            
            if len(q) > k and q[k]['dirty'] == True:  # use 'dirty' to check if there is real data inside, otherwise max() not work when q item just changes but before filled any data
#                 print self.lines[k*20]
#                 print self.lines

                self.lines[k*20].set_xdata(q[k]['data']["time"]) 
                self.lines[k*20].set_ydata(q[k]['data']['price']) 
                self.lines[k*20].set_label('price_%s' %q[k]['cmd']["price"])            
                self.lines[k*20+1].set_xdata(q[k]['data']["time"])
                self.lines[k*20+1].set_ydata(q[k]['data']['vol'])
                self.lines[k*20+1].set_label('vol')
                
                i=0  # used for trace the MA type in 'data'
                legend1=[];legend2=[]  #used for dynamic udpate legend
                legend1.append(self.lines[k*20].get_label()) 
                legend2.append(self.lines[k*20+1].get_label()) 
                if '1s' in q[k]['cmd']['movingave']:
                    self.lines[k*20+2].set_xdata(q[k]['data']["time"])       
                    self.lines[k*20+2].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma1 value    # issue: it's better change 'ma' in q as dict, so that here we only need grab ma data from q instead of create new list(trade off between network bw and local calc)
                    self.lines[k*20+2].set_label('MA_1s')
                    self.lines[k*20+3].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+3].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma1 vol
                    self.lines[k*20+3].set_label('Vol_MA_1s')
                    i=i+1       
                    legend1.append(self.lines[k*20+2].get_label()) 
                    legend2.append(self.lines[k*20+3].get_label())    
                if '5s' in q[k]['cmd']['movingave']:
                    self.lines[k*20+4].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+4].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma2 value
                    self.lines[k*20+4].set_label('MA_5s')
                    self.lines[k*20+5].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+5].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma2 vol
                    self.lines[k*20+5].set_label('Vol_MA_5s' )
                    i=i+1
                    legend1.append(self.lines[k*20+4].get_label()) 
                    legend2.append(self.lines[k*20+5].get_label()) 
                if '10s' in q[k]['cmd']['movingave']:
                    self.lines[k*20+6].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+6].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma3 value
                    self.lines[k*20+6].set_label('MA_10s' )
                    self.lines[k*20+7].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+7].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma3 vol
                    self.lines[k*20+7].set_label('Vol_MA_10s')
                    i=i+1
                    legend1.append(self.lines[k*20+7].get_label()) 
                    legend2.append(self.lines[k*20+7].get_label())
                if '30s' in q[k]['cmd']['movingave']:
                    self.lines[k*20+8].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+8].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma4 value
                    self.lines[k*20+8].set_label('MA_30s' )
                    self.lines[k*20+9].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+9].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma4 vol
                    self.lines[k*20+9].set_label('Vol_MA_30s' )
                    i=i+1
                    legend1.append(self.lines[k*20+8].get_label()) 
                    legend2.append(self.lines[k*20+9].get_label())
                if '1m' in q[k]['cmd']['movingave']:
                    self.lines[k*20+10].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+10].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma5 value
                    self.lines[k*20+10].set_label('MA_1m' )
                    self.lines[k*20+11].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+11].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma5 vol
                    self.lines[k*20+11].set_label('Vol_MA_1m') 
                    i=i+1
                    legend1.append(self.lines[k*20+10].get_label()) 
                    legend2.append(self.lines[k*20+11].get_label())
                if '5m' in q[k]['cmd']['movingave']:
                    self.lines[k*20+12].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+12].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma6 value
                    self.lines[k*20+12].set_label('MA_5m')
                    self.lines[k*20+13].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+13].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma6 vol
                    self.lines[k*20+13].set_label('Vol_MA_5m' ) 
                    i=i+1  
                    legend1.append(self.lines[k*20+12].get_label()) 
                    legend2.append(self.lines[k*20+13].get_label())         
                if '10m' in q[k]['cmd']['movingave']:
                    self.lines[k*20+14].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+14].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma7 value
                    self.lines[k*20+14].set_label('MA_10m' )
                    self.lines[k*20+15].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+15].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma7 value
                    self.lines[k*20+15].set_label('Vol_MA_10m' ) 
                    i=i+1 
                    legend1.append(self.lines[k*20+14].get_label()) 
                    legend2.append(self.lines[k*20+15].get_label())
                if '30m' in q[k]['cmd']['movingave']:
                    self.lines[k*20+16].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+16].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma8 value
                    self.lines[k*20+16].set_label('MA_30m' )
                    self.lines[k*20+17].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+17].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma8 value
                    self.lines[k*20+17].set_label('Vol_MA_30m')  
                    i=i+1  
                    legend1.append(self.lines[k*20+16].get_label()) 
                    legend2.append(self.lines[k*20+17].get_label())  
                if '1h' in q[k]['cmd']['movingave']:
                    self.lines[k*20+18].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+18].set_ydata([j[i].split(':')[0] for j in q[k]['data']["ma"]])  # ma9 value
                    self.lines[k*20+18].set_label('MA_1h' )
                    self.lines[k*20+19].set_xdata(q[k]['data']["time"])
                    self.lines[k*20+19].set_ydata([j[i].split(':')[1] for j in q[k]['data']["ma"]])  # ma9 value
                    self.lines[k*20+19].set_label('Vol_MA_1h') 
                    legend1.append(self.lines[k*20+18].get_label()) 
                    legend2.append(self.lines[k*20+19].get_label())  
                     
                self.axarr[k*2].set_ylim(0.5 * min(q[k]['data']['price']), 1.5 * max(q[k]['data']['price']))  # dynamic adj the y limi here!
                self.axarr[k*2+1].set_ylim(0, 1.5 * max(q[k]['data']['vol']))
     
                if q[k]['cmd']['type'] == 'h':  # realtime xlim will be set in other block
                    self.reset_xlim_history(k)
                else:
                    self.axarr[k*2].set_xticks([matplotlib.dates.num2date(q[k]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[k]['cmd']['interval'])) for i in range(10)])  
                    self.axarr[k*2+1].set_xticks([matplotlib.dates.num2date(q[k]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[k]['cmd']['interval'])) for i in range(10)])                  
                    self.axarr[k*2+1].set_xticklabels([(matplotlib.dates.num2date(q[k]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[k]['cmd']['interval']))).strftime('%H:%M:%S') for i in range(10)],rotation=0,size='xx-small',)
                 
                ## set labels
                self.axarr[k*2].set_title('id:%s, symbol: %s_%s, interv: %s, price=%.2f, vol=%.2f' % (k,q[k]['cmd']['symbol'], q[k]['cmd']['type'], q[k]['cmd']['interval'], q[k]['data']['price'][-1], q[k]['data']['vol'][-1]),y=0.9)
                self.axarr[k*2].legend(legend1, fontsize='small')  # auto update legend, in case subplot insertion cause legend number change
                self.axarr[k*2+1].legend(legend2, fontsize='x-small')  # in some matplotlib version, we need remove 'handles' name inside legend()
#                 
#                
           
#         # Update 2nd subplot data
#         if len(q) > 1 and q[1]['dirty'] == True:  
#             self.lines21.set_xdata(q[1]['data']["time"])  
#             self.lines21.set_ydata(q[1]['data']['price'])  
#             self.lines21.set_label('price_%s' %q[1]['cmd']["price"])       
#             self.lines22.set_xdata(q[1]['data']["time"])
#             self.lines22.set_ydata(q[1]['data']['vol'])
#             self.lines22.set_label('vol')
#             i=0
#             legend1=[];legend2=[]
#             legend1.append(self.lines21.get_label()) 
#             legend2.append(self.lines22.get_label()) 
#             if '1s' in q[1]['cmd']['movingave']:
#                 self.lines23.set_xdata(q[1]['data']["time"])      
#                 self.lines23.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma1 value    
#                 self.lines23.set_label('MA_1s')
#                 self.lines24.set_xdata(q[1]['data']["time"])
#                 self.lines24.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma1 vol
#                 self.lines24.set_label('Vol_MA_1s') 
#                 i=i+1   
#                 legend1.append(self.lines23.get_label()) 
#                 legend2.append(self.lines24.get_label())   
#             if '5s' in q[1]['cmd']['movingave']:
#                 self.lines25.set_xdata(q[1]['data']["time"])
#                 self.lines25.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma2 value
#                 self.lines25.set_label('MA_5s')
#                 self.lines26.set_xdata(q[1]['data']["time"])
#                 self.lines26.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma2 vol
#                 self.lines26.set_label('Vol_MA_5s' )
#                 i=i+1
#                 legend1.append(self.lines25.get_label()) 
#                 legend2.append(self.lines26.get_label())     
#             if '10s' in q[1]['cmd']['movingave']:
#                 self.lines27.set_xdata(q[1]['data']["time"])
#                 self.lines27.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma3 value
#                 self.lines27.set_label('MA_10s' )
#                 self.lines28.set_xdata(q[1]['data']["time"])
#                 self.lines28.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma3 vol
#                 self.lines28.set_label('Vol_MA_10s')
#                 i=i+1
#                 legend1.append(self.lines27.get_label()) 
#                 legend2.append(self.lines28.get_label()) 
#             if '30s' in q[1]['cmd']['movingave']:
#                 self.lines29.set_xdata(q[1]['data']["time"])
#                 self.lines29.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma4 value
#                 self.lines29.set_label('MA_30s' )
#                 self.lines2a.set_xdata(q[1]['data']["time"])
#                 self.lines2a.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma4 vol
#                 self.lines2a.set_label('Vol_MA_30s' )
#                 i=i+1
#                 legend1.append(self.lines29.get_label()) 
#                 legend2.append(self.lines2a.get_label()) 
#             if '1m' in q[1]['cmd']['movingave']:
#                 self.lines2b.set_xdata(q[1]['data']["time"])
#                 self.lines2b.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma5 value
#                 self.lines2b.set_label('MA_1m' )
#                 self.lines2c.set_xdata(q[1]['data']["time"])
#                 self.lines2c.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma5 vol
#                 self.lines2c.set_label('Vol_MA_1m')
#                 i=i+1
#                 legend1.append(self.lines2b.get_label()) 
#                 legend2.append(self.lines2c.get_label()) 
#             if '5m' in q[1]['cmd']['movingave']:
#                 self.lines2d.set_xdata(q[1]['data']["time"])
#                 self.lines2d.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma6 value
#                 self.lines2d.set_label('MA_5m')
#                 self.lines2e.set_xdata(q[1]['data']["time"])
#                 self.lines2e.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma6 vol
#                 self.lines2e.set_label('Vol_MA_5m' )  
#                 i=i+1
#                 legend1.append(self.lines2d.get_label()) 
#                 legend2.append(self.lines2e.get_label()) 
#             if '10m' in q[1]['cmd']['movingave']:
#                 self.lines2f.set_xdata(q[1]['data']["time"])
#                 self.lines2f.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma7 value
#                 self.lines2f.set_label('MA_10m' )
#                 self.lines2g.set_xdata(q[1]['data']["time"])
#                 self.lines2g.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma7 value
#                 self.lines2g.set_label('Vol_MA_10m' ) 
#                 i=i+1
#                 legend1.append(self.lines2f.get_label()) 
#                 legend2.append(self.lines2g.get_label())    
#             if '30m' in q[1]['cmd']['movingave']:
#                 self.lines2h.set_xdata(q[1]['data']["time"])
#                 self.lines2h.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma8 value
#                 self.lines2h.set_label('MA_30m' )
#                 self.lines2i.set_xdata(q[1]['data']["time"])
#                 self.lines2i.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma8 value
#                 self.lines2i.set_label('Vol_MA_30m') 
#                 i=i+1 
#                 legend1.append(self.lines2h.get_label()) 
#                 legend2.append(self.lines2i.get_label())       
#             if '1h' in q[1]['cmd']['movingave']:
#                 self.lines2j.set_xdata(q[1]['data']["time"])
#                 self.lines2j.set_ydata([j[i].split(':')[0] for j in q[1]['data']["ma"]])  # ma9 value
#                 self.lines2j.set_label('MA_1h' )
#                 self.lines2k.set_xdata(q[1]['data']["time"])
#                 self.lines2k.set_ydata([j[i].split(':')[1] for j in q[1]['data']["ma"]])  # ma9 value
#                 self.lines2k.set_label('Vol_MA_1h') 
#                 legend1.append(self.lines2j.get_label()) 
#                 legend2.append(self.lines2k.get_label())   
#               
#             self.axarr[2].set_ylim(0.5 * min(q[1]['data']['price']), 1.5 * max(q[1]['data']['price']))
#             self.axarr[3].set_ylim(0, 1.5 * max(q[1]['data']['vol']))
#             
#             if q[1]['cmd']['type'] == 'h':
#                 self.reset_xlim_history(1)
#             else:
#                 self.axarr[2].set_xticks([matplotlib.dates.num2date(q[1]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[1]['cmd']['interval'])) for i in range(10)])  
#                 self.axarr[3].set_xticks([matplotlib.dates.num2date(q[1]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[1]['cmd']['interval'])) for i in range(10)])                  
#                 self.axarr[3].set_xticklabels([(matplotlib.dates.num2date(q[1]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[1]['cmd']['interval']))).strftime('%H:%M:%S') for i in range(10)],rotation=0,size='xx-small',)
#             
#             self.axarr[2].set_title('id:2, symbol: %s_%s, interv: %s, price=%.2f, vol=%.2f' % (q[1]['cmd']['symbol'], q[1]['cmd']['type'], q[1]['cmd']['interval'], q[1]['data']['price'][-1], q[1]['data']['vol'][-1]),y=0.85,fontsize='medium') 
#             self.axarr[2].legend(legend1,fontsize='x-small')
#             self.axarr[3].legend(legend2,fontsize='xx-small')
#             
#         # Update 3rd subplot data
#         if len(q) > 2 and q[2]['dirty'] == True:  
#             self.lines31.set_xdata(q[2]['data']["time"])  
#             self.lines31.set_ydata(q[2]['data']['price'])  
#             self.lines31.set_label('price_%s' %q[2]['cmd']["price"])       
#             self.lines32.set_xdata(q[2]['data']["time"])
#             self.lines32.set_ydata(q[2]['data']['vol'])
#             self.lines32.set_label('vol')
#             i=0
#             legend1=[];legend2=[]
#             legend1.append(self.lines31.get_label()) 
#             legend2.append(self.lines32.get_label())
#             if '1s' in q[2]['cmd']['movingave']:
#                 self.lines33.set_xdata(q[2]['data']["time"])      
#                 self.lines33.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma1 value    
#                 self.lines33.set_label('MA_1s')
#                 self.lines34.set_xdata(q[2]['data']["time"])
#                 self.lines34.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma1 vol
#                 self.lines34.set_label('Vol_MA_1s')   
#                 i=i+1 
#                 legend1.append(self.lines33.get_label()) 
#                 legend2.append(self.lines34.get_label())  
#             if '5s' in q[2]['cmd']['movingave']:
#                 self.lines35.set_xdata(q[2]['data']["time"])
#                 self.lines35.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma2 value
#                 self.lines35.set_label('MA_5s')
#                 self.lines36.set_xdata(q[2]['data']["time"])
#                 self.lines36.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma2 vol
#                 self.lines36.set_label('Vol_MA_5s' )   
#                 i=i+1
#                 legend1.append(self.lines35.get_label()) 
#                 legend2.append(self.lines36.get_label()) 
#             if '10s' in q[2]['cmd']['movingave']:
#                 self.lines37.set_xdata(q[2]['data']["time"])
#                 self.lines37.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma3 value
#                 self.lines37.set_label('MA_10s' )
#                 self.lines38.set_xdata(q[2]['data']["time"])
#                 self.lines38.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma3 vol
#                 self.lines38.set_label('Vol_MA_10s')
#                 i=i+1
#                 legend1.append(self.lines37.get_label()) 
#                 legend2.append(self.lines38.get_label())
#             if '30s' in q[2]['cmd']['movingave']:
#                 self.lines39.set_xdata(q[2]['data']["time"])
#                 self.lines39.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma4 value
#                 self.lines39.set_label('MA_30s' )
#                 self.lines3a.set_xdata(q[2]['data']["time"])
#                 self.lines3a.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma4 vol
#                 self.lines3a.set_label('Vol_MA_30s' )
#                 i=i+1
#                 legend1.append(self.lines39.get_label()) 
#                 legend2.append(self.lines3a.get_label())
#             if '1m' in q[2]['cmd']['movingave']:
#                 self.lines3b.set_xdata(q[2]['data']["time"])
#                 self.lines3b.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma5 value
#                 self.lines3b.set_label('MA_1m' )
#                 self.lines3c.set_xdata(q[2]['data']["time"])
#                 self.lines3c.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma5 vol
#                 self.lines3c.set_label('Vol_MA_1m')
#                 i=i+1
#                 legend1.append(self.lines3b.get_label()) 
#                 legend2.append(self.lines3c.get_label())
#             if '5m' in q[2]['cmd']['movingave']:
#                 self.lines3d.set_xdata(q[2]['data']["time"])
#                 self.lines3d.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma6 value
#                 self.lines3d.set_label('MA_5m')
#                 self.lines3e.set_xdata(q[2]['data']["time"])
#                 self.lines3e.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma6 vol
#                 self.lines3e.set_label('Vol_MA_5m' )
#                 i=i+1 
#                 legend1.append(self.lines3d.get_label()) 
#                 legend2.append(self.lines3e.get_label()) 
#             if '10m' in q[2]['cmd']['movingave']:
#                 self.lines3f.set_xdata(q[2]['data']["time"])
#                 self.lines3f.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma7 value
#                 self.lines3f.set_label('MA_10m' )
#                 self.lines3g.set_xdata(q[2]['data']["time"])
#                 self.lines3g.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma7 value
#                 self.lines3g.set_label('Vol_MA_10m' ) 
#                 i=i+1   
#                 legend1.append(self.lines3f.get_label()) 
#                 legend2.append(self.lines3g.get_label())
#             if '30m' in q[2]['cmd']['movingave']:
#                 self.lines3h.set_xdata(q[2]['data']["time"])
#                 self.lines3h.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma8 value
#                 self.lines3h.set_label('MA_30m' )
#                 self.lines3i.set_xdata(q[2]['data']["time"])
#                 self.lines3i.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma8 value
#                 self.lines3i.set_label('Vol_MA_30m')  
#                 i=i+1  
#                 legend1.append(self.lines3h.get_label()) 
#                 legend2.append(self.lines3i.get_label())    
#             if '1h' in q[2]['cmd']['movingave']:
#                 self.lines3j.set_xdata(q[2]['data']["time"])
#                 self.lines3j.set_ydata([j[i].split(':')[0] for j in q[2]['data']["ma"]])  # ma9 value
#                 self.lines3j.set_label('MA_1h' )
#                 self.lines3k.set_xdata(q[2]['data']["time"])
#                 self.lines3k.set_ydata([j[i].split(':')[1] for j in q[2]['data']["ma"]])  # ma9 value
#                 self.lines3k.set_label('Vol_MA_1h')   
#                 legend1.append(self.lines3j.get_label()) 
#                 legend2.append(self.lines3k.get_label())
#                 
#             self.axarr[4].set_ylim(0.5 * min(q[2]['data']['price']), 1.5 * max(q[2]['data']['price']))
#             self.axarr[5].set_ylim(0, 1.5 * max(q[2]['data']['vol']))
#             
#             if q[2]['cmd']['type'] == 'h':
#                 self.reset_xlim_history(2)
#             else:
#                 self.axarr[4].set_xticks([matplotlib.dates.num2date(q[2]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[2]['cmd']['interval'])) for i in range(10)])  
#                 self.axarr[5].set_xticks([matplotlib.dates.num2date(q[2]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[2]['cmd']['interval'])) for i in range(10)])                  
#                 self.axarr[5].set_xticklabels([(matplotlib.dates.num2date(q[2]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[2]['cmd']['interval']))).strftime('%H:%M:%S') for i in range(10)],rotation=0,size='xx-small',)
#             
#             self.axarr[4].set_title('id:3, symbol: %s_%s, interv: %s, price=%.2f, vol=%.2f' % (q[2]['cmd']['symbol'], q[2]['cmd']['type'], q[2]['cmd']['interval'], q[2]['data']['price'][-1], q[2]['data']['vol'][-1]),y=0.85,fontsize='medium') 
#             self.axarr[4].legend(legend1,fontsize='x-small')
#             self.axarr[5].legend(legend2,fontsize='xx-small')
#             
#         
#         # Update 4th subplot data
#         if len(q) > 3 and q[3]['dirty'] == True:  
#             self.lines41.set_xdata(q[3]['data']["time"])  
#             self.lines41.set_ydata(q[3]['data']['price'])  
#             self.lines41.set_label('price_%s' %q[3]['cmd']["price"])       
#             self.lines42.set_xdata(q[3]['data']["time"])
#             self.lines42.set_ydata(q[3]['data']['vol'])
#             self.lines42.set_label('vol')
#             i=0
#             legend1=[];legend2=[]
#             legend1.append(self.lines41.get_label()) 
#             legend2.append(self.lines42.get_label())
#             if '1s' in q[3]['cmd']['movingave']:
#                 self.lines43.set_xdata(q[3]['data']["time"])      
#                 self.lines43.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma1 value    
#                 self.lines43.set_label('MA_1s')
#                 self.lines44.set_xdata(q[3]['data']["time"])
#                 self.lines44.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma1 vol
#                 self.lines44.set_label('Vol_MA_1s')  
#                 i=i+1 
#                 legend1.append(self.lines43.get_label()) 
#                 legend2.append(self.lines44.get_label())   
#             if '5s' in q[3]['cmd']['movingave']:
#                 self.lines45.set_xdata(q[3]['data']["time"])
#                 self.lines45.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma2 value
#                 self.lines45.set_label('MA_5s')
#                 self.lines46.set_xdata(q[3]['data']["time"])
#                 self.lines46.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma2 vol
#                 self.lines46.set_label('Vol_MA_5s' ) 
#                 i=i+1  
#                 legend1.append(self.lines45.get_label()) 
#                 legend2.append(self.lines46.get_label())  
#             if '10s' in q[3]['cmd']['movingave']:
#                 self.lines47.set_xdata(q[3]['data']["time"])
#                 self.lines47.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma3 value
#                 self.lines47.set_label('MA_10s' )
#                 self.lines48.set_xdata(q[3]['data']["time"])
#                 self.lines48.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma3 vol
#                 self.lines48.set_label('Vol_MA_10s')
#                 i=i+1
#                 legend1.append(self.lines47.get_label()) 
#                 legend2.append(self.lines48.get_label()) 
#             if '30s' in q[3]['cmd']['movingave']:
#                 self.lines49.set_xdata(q[3]['data']["time"])
#                 self.lines49.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma4 value
#                 self.lines49.set_label('MA_30s' )
#                 self.lines4a.set_xdata(q[3]['data']["time"])
#                 self.lines4a.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma4 vol
#                 self.lines4a.set_label('Vol_MA_30s' )
#                 i=i+1
#                 legend1.append(self.lines49.get_label()) 
#                 legend2.append(self.lines4a.get_label()) 
#             if '1m' in q[3]['cmd']['movingave']:
#                 self.lines4b.set_xdata(q[3]['data']["time"])
#                 self.lines4b.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma5 value
#                 self.lines4b.set_label('MA_1m' )
#                 self.lines4c.set_xdata(q[3]['data']["time"])
#                 self.lines4c.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma5 vol
#                 self.lines4c.set_label('Vol_MA_1m')
#                 i=i+1
#                 legend1.append(self.lines4b.get_label()) 
#                 legend2.append(self.lines4c.get_label()) 
#             if '5m' in q[3]['cmd']['movingave']:
#                 self.lines4d.set_xdata(q[3]['data']["time"])
#                 self.lines4d.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma6 value
#                 self.lines4d.set_label('MA_5m')
#                 self.lines4e.set_xdata(q[3]['data']["time"])
#                 self.lines4e.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma6 vol
#                 self.lines4e.set_label('Vol_MA_5m' ) 
#                 i=i+1 
#                 legend1.append(self.lines4d.get_label()) 
#                 legend2.append(self.lines4e.get_label()) 
#             if '10m' in q[3]['cmd']['movingave']:
#                 self.lines4f.set_xdata(q[3]['data']["time"])
#                 self.lines4f.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma7 value
#                 self.lines4f.set_label('MA_10m' )
#                 self.lines4g.set_xdata(q[3]['data']["time"])
#                 self.lines4g.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma7 value
#                 self.lines4g.set_label('Vol_MA_10m' ) 
#                 i=i+1  
#                 legend1.append(self.lines4f.get_label()) 
#                 legend2.append(self.lines4g.get_label())  
#             if '30m' in q[3]['cmd']['movingave']:
#                 self.lines4h.set_xdata(q[3]['data']["time"])
#                 self.lines4h.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma8 value
#                 self.lines4h.set_label('MA_30m' )
#                 self.lines4i.set_xdata(q[3]['data']["time"])
#                 self.lines4i.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma8 value
#                 self.lines4i.set_label('Vol_MA_30m') 
#                 i=i+1      
#                 legend1.append(self.lines4h.get_label()) 
#                 legend2.append(self.lines4i.get_label())  
#             if '1h' in q[3]['cmd']['movingave']:
#                 self.lines4j.set_xdata(q[3]['data']["time"])
#                 self.lines4j.set_ydata([j[i].split(':')[0] for j in q[3]['data']["ma"]])  # ma9 value
#                 self.lines4j.set_label('MA_1h' )
#                 self.lines4k.set_xdata(q[3]['data']["time"])
#                 self.lines4k.set_ydata([j[i].split(':')[1] for j in q[3]['data']["ma"]])  # ma9 value
#                 self.lines4k.set_label('Vol_MA_1h') 
#                 legend1.append(self.lines4j.get_label()) 
#                 legend2.append(self.lines4k.get_label())   
#               
#             self.axarr[6].set_ylim(0.5 * min(q[3]['data']['price']), 1.5 * max(q[3]['data']['price']))
#             self.axarr[7].set_ylim(0, 1.5 * max(q[3]['data']['vol']))
#             
#             if q[3]['cmd']['type'] == 'h':
#                 self.reset_xlim_history(3)
#             else:
#                 self.axarr[6].set_xticks([matplotlib.dates.num2date(q[3]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[3]['cmd']['interval'])) for i in range(10)])  
#                 self.axarr[7].set_xticks([matplotlib.dates.num2date(q[3]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[3]['cmd']['interval'])) for i in range(10)])                  
#                 self.axarr[7].set_xticklabels([(matplotlib.dates.num2date(q[3]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[3]['cmd']['interval']))).strftime('%H:%M:%S') for i in range(10)],rotation=0,size='xx-small',)
#             
#             self.axarr[6].set_title('id:4, symbol: %s_%s, interv: %s, price=%.2f, vol=%.2f' % (q[3]['cmd']['symbol'], q[3]['cmd']['type'], q[3]['cmd']['interval'], q[3]['data']['price'][-1], q[3]['data']['vol'][-1]),y=0.85,fontsize='medium') 
#             self.axarr[6].legend(legend1,fontsize='x-small')
#             self.axarr[7].legend(legend2,fontsize='xx-small')
#             
#         
#         # Update 5th subplot data
#         if len(q) > 4 and q[4]['dirty'] == True:  
#             self.lines51.set_xdata(q[4]['data']["time"])  
#             self.lines51.set_ydata(q[4]['data']['price'])  
#             self.lines51.set_label('price_%s' %q[4]['cmd']["price"])       
#             self.lines52.set_xdata(q[4]['data']["time"])
#             self.lines52.set_ydata(q[4]['data']['vol'])
#             self.lines52.set_label('vol')
#             i=0
#             legend1=[];legend2=[]
#             legend1.append(self.lines51.get_label()) 
#             legend2.append(self.lines52.get_label()) 
#             if '1s' in q[4]['cmd']['movingave']:
#                 self.lines53.set_xdata(q[4]['data']["time"])      
#                 self.lines53.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma1 value    
#                 self.lines53.set_label('MA_1s')
#                 self.lines54.set_xdata(q[4]['data']["time"])
#                 self.lines54.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma1 vol
#                 self.lines54.set_label('Vol_MA_1s') 
#                 i=i+1
#                 legend1.append(self.lines53.get_label()) 
#                 legend2.append(self.lines54.get_label())     
#             if '5s' in q[4]['cmd']['movingave']:
#                 self.lines55.set_xdata(q[4]['data']["time"])
#                 self.lines55.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma2 value
#                 self.lines55.set_label('MA_5s')
#                 self.lines56.set_xdata(q[4]['data']["time"])
#                 self.lines56.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma2 vol
#                 self.lines56.set_label('Vol_MA_5s' ) 
#                 i=i+1
#                 legend1.append(self.lines55.get_label()) 
#                 legend2.append(self.lines56.get_label())   
#             if '10s' in q[4]['cmd']['movingave']:
#                 self.lines57.set_xdata(q[4]['data']["time"])
#                 self.lines57.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma3 value
#                 self.lines57.set_label('MA_10s' )
#                 self.lines58.set_xdata(q[4]['data']["time"])
#                 self.lines58.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma3 vol
#                 self.lines58.set_label('Vol_MA_10s')
#                 i=i+1
#                 legend1.append(self.lines57.get_label()) 
#                 legend2.append(self.lines58.get_label())
#             if '30s' in q[4]['cmd']['movingave']:
#                 self.lines59.set_xdata(q[4]['data']["time"])
#                 self.lines59.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma4 value
#                 self.lines59.set_label('MA_30s' )
#                 self.lines5a.set_xdata(q[4]['data']["time"])
#                 self.lines5a.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma4 vol
#                 self.lines5a.set_label('Vol_MA_30s' )
#                 i=i+1
#                 legend1.append(self.lines59.get_label()) 
#                 legend2.append(self.lines5a.get_label())
#             if '1m' in q[4]['cmd']['movingave']:
#                 self.lines5b.set_xdata(q[4]['data']["time"])
#                 self.lines5b.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma5 value
#                 self.lines5b.set_label('MA_1m' )
#                 self.lines5c.set_xdata(q[4]['data']["time"])
#                 self.lines5c.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma5 vol
#                 self.lines5c.set_label('Vol_MA_1m')
#                 i=i+1
#                 legend1.append(self.lines5b.get_label()) 
#                 legend2.append(self.lines5c.get_label())
#             if '5m' in q[4]['cmd']['movingave']:
#                 self.lines5d.set_xdata(q[4]['data']["time"])
#                 self.lines5d.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma6 value
#                 self.lines5d.set_label('MA_5m')
#                 self.lines5e.set_xdata(q[4]['data']["time"])
#                 self.lines5e.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma6 vol
#                 self.lines5e.set_label('Vol_MA_5m' )  
#                 i=i+1
#                 legend1.append(self.lines5d.get_label()) 
#                 legend2.append(self.lines5e.get_label())
#             if '10m' in q[4]['cmd']['movingave']:
#                 self.lines5f.set_xdata(q[4]['data']["time"])
#                 self.lines5f.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma7 value
#                 self.lines5f.set_label('MA_10m' )
#                 self.lines5g.set_xdata(q[4]['data']["time"])
#                 self.lines5g.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma7 value
#                 self.lines5g.set_label('Vol_MA_10m' ) 
#                 i=i+1   
#                 legend1.append(self.lines5f.get_label()) 
#                 legend2.append(self.lines5g.get_label())
#             if '30m' in q[4]['cmd']['movingave']:
#                 self.lines5h.set_xdata(q[4]['data']["time"])
#                 self.lines5h.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma8 value
#                 self.lines5h.set_label('MA_30m' )
#                 self.lines5i.set_xdata(q[4]['data']["time"])
#                 self.lines5i.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma8 value
#                 self.lines5i.set_label('Vol_MA_30m')  
#                 i=i+1      
#                 legend1.append(self.lines5h.get_label()) 
#                 legend2.append(self.lines5i.get_label())
#             if '1h' in q[4]['cmd']['movingave']:
#                 self.lines5j.set_xdata(q[4]['data']["time"])
#                 self.lines5j.set_ydata([j[i].split(':')[0] for j in q[4]['data']["ma"]])  # ma9 value
#                 self.lines5j.set_label('MA_1h' )
#                 self.lines5k.set_xdata(q[4]['data']["time"])
#                 self.lines5k.set_ydata([j[i].split(':')[1] for j in q[4]['data']["ma"]])  # ma9 value
#                 self.lines5k.set_label('Vol_MA_1h')   
#                 legend1.append(self.lines5j.get_label()) 
#                 legend2.append(self.lines5k.get_label())
#             self.axarr[8].set_ylim(0.5 * min(q[4]['data']['price']), 1.5 * max(q[4]['data']['price']))
#             self.axarr[9].set_ylim(0, 1.5 * max(q[4]['data']['vol']))
#             
#             if q[4]['cmd']['type'] == 'h':
#                 self.reset_xlim_history(5)
#             else:
#                 self.axarr[8].set_xticks([matplotlib.dates.num2date(q[4]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[4]['cmd']['interval'])) for i in range(10)])  
#                 self.axarr[9].set_xticks([matplotlib.dates.num2date(q[4]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[4]['cmd']['interval'])) for i in range(10)])                  
#                 self.axarr[9].set_xticklabels([(matplotlib.dates.num2date(q[4]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[4]['cmd']['interval']))).strftime('%H:%M:%S') for i in range(10)],rotation=0,size='xx-small',)
#             
#             self.axarr[8].set_title('id:5, symbol: %s_%s, interv: %s, price=%.2f, vol=%.2f' % (q[4]['cmd']['symbol'], q[4]['cmd']['type'], q[4]['cmd']['interval'], q[4]['data']['price'][-1], q[4]['data']['vol'][-1]),y=0.85,fontsize='medium') 
#             self.axarr[8].legend(legend1,fontsize='x-small')
#             self.axarr[9].legend(legend2,fontsize='xx-small')
#             
#         
#         # Update 6th subplot data
#         if len(q) > 5 and q[5]['dirty'] == True:  
#             self.lines61.set_xdata(q[5]['data']["time"])  
#             self.lines61.set_ydata(q[5]['data']['price'])  
#             self.lines61.set_label('price_%s' %q[5]['cmd']["price"])       
#             self.lines62.set_xdata(q[5]['data']["time"])
#             self.lines62.set_ydata(q[5]['data']['vol'])
#             self.lines62.set_label('vol')
#             i=0
#             legend1=[];legend2=[]
#             legend1.append(self.lines61.get_label()) 
#             legend2.append(self.lines62.get_label())
#             if '1s' in q[5]['cmd']['movingave']:
#                 self.lines63.set_xdata(q[5]['data']["time"])      
#                 self.lines63.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma1 value    
#                 self.lines63.set_label('MA_1s')
#                 self.lines64.set_xdata(q[5]['data']["time"])
#                 self.lines64.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma1 vol
#                 self.lines64.set_label('Vol_MA_1s') 
#                 i=i+1
#                 legend1.append(self.lines63.get_label()) 
#                 legend2.append(self.lines64.get_label())     
#             if '5s' in q[5]['cmd']['movingave']:
#                 self.lines65.set_xdata(q[5]['data']["time"])
#                 self.lines65.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma2 value
#                 self.lines65.set_label('MA_5s')
#                 self.lines66.set_xdata(q[5]['data']["time"])
#                 self.lines66.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma2 vol
#                 self.lines66.set_label('Vol_MA_5s' )  
#                 i=i+1
#                 legend1.append(self.lines65.get_label()) 
#                 legend2.append(self.lines66.get_label())  
#             if '10s' in q[5]['cmd']['movingave']:
#                 self.lines67.set_xdata(q[5]['data']["time"])
#                 self.lines67.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma3 value
#                 self.lines67.set_label('MA_10s' )
#                 self.lines68.set_xdata(q[5]['data']["time"])
#                 self.lines68.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma3 vol
#                 self.lines68.set_label('Vol_MA_10s')
#                 i=i+1
#                 legend1.append(self.lines67.get_label()) 
#                 legend2.append(self.lines68.get_label())
#             if '30s' in q[5]['cmd']['movingave']:
#                 self.lines69.set_xdata(q[5]['data']["time"])
#                 self.lines69.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma4 value
#                 self.lines69.set_label('MA_30s' )
#                 self.lines6a.set_xdata(q[5]['data']["time"])
#                 self.lines6a.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma4 vol
#                 self.lines6a.set_label('Vol_MA_30s' )
#                 i=i+1
#                 legend1.append(self.lines69.get_label()) 
#                 legend2.append(self.lines6a.get_label())
#             if '1m' in q[5]['cmd']['movingave']:
#                 self.lines6b.set_xdata(q[5]['data']["time"])
#                 self.lines6b.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma5 value
#                 self.lines6b.set_label('MA_1m' )
#                 self.lines6c.set_xdata(q[5]['data']["time"])
#                 self.lines6c.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma5 vol
#                 self.lines6c.set_label('Vol_MA_1m')
#                 i=i+1
#                 legend1.append(self.lines6b.get_label()) 
#                 legend2.append(self.lines6c.get_label())
#             if '5m' in q[5]['cmd']['movingave']:
#                 self.lines6d.set_xdata(q[5]['data']["time"])
#                 self.lines6d.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma6 value
#                 self.lines6d.set_label('MA_5m')
#                 self.lines6e.set_xdata(q[5]['data']["time"])
#                 self.lines6e.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma6 vol
#                 self.lines6e.set_label('Vol_MA_5m' ) 
#                 i=i+1 
#                 legend1.append(self.lines6d.get_label()) 
#                 legend2.append(self.lines6e.get_label())
#             if '10m' in q[5]['cmd']['movingave']:
#                 self.lines6f.set_xdata(q[5]['data']["time"])
#                 self.lines6f.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma7 value
#                 self.lines6f.set_label('MA_10m' )
#                 self.lines6g.set_xdata(q[5]['data']["time"])
#                 self.lines6g.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma7 value
#                 self.lines6g.set_label('Vol_MA_10m' )  
#                 i=i+1  
#                 legend1.append(self.lines6f.get_label()) 
#                 legend2.append(self.lines6g.get_label())
#             if '30m' in q[5]['cmd']['movingave']:
#                 self.lines6h.set_xdata(q[5]['data']["time"])
#                 self.lines6h.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma8 value
#                 self.lines6h.set_label('MA_30m' )
#                 self.lines6i.set_xdata(q[5]['data']["time"])
#                 self.lines6i.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma8 value
#                 self.lines6i.set_label('Vol_MA_30m') 
#                 i=i+1       
#                 legend1.append(self.lines6h.get_label()) 
#                 legend2.append(self.lines6i.get_label())
#             if '1h' in q[5]['cmd']['movingave']:
#                 self.lines6j.set_xdata(q[5]['data']["time"])
#                 self.lines6j.set_ydata([j[i].split(':')[0] for j in q[5]['data']["ma"]])  # ma9 value
#                 self.lines6j.set_label('MA_1h' )
#                 self.lines6k.set_xdata(q[5]['data']["time"])
#                 self.lines6k.set_ydata([j[i].split(':')[1] for j in q[5]['data']["ma"]])  # ma9 value
#                 self.lines6k.set_label('Vol_MA_1h')   
#                 legend1.append(self.lines6j.get_label()) 
#                 legend2.append(self.lines6k.get_label())
#                 
#             self.axarr[10].set_ylim(0.5 * min(q[5]['data']['price']), 1.5 * max(q[5]['data']['price']))
#             self.axarr[11].set_ylim(0, 1.5 * max(q[5]['data']['vol']))
#             
#             if q[5]['cmd']['type'] == 'h':
#                 self.reset_xlim_history(5)
#             else:
#                 self.axarr[10].set_xticks([matplotlib.dates.num2date(q[5]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[5]['cmd']['interval'])) for i in range(10)])  
#                 self.axarr[11].set_xticks([matplotlib.dates.num2date(q[5]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[5]['cmd']['interval'])) for i in range(10)])                  
#                 self.axarr[11].set_xticklabels([(matplotlib.dates.num2date(q[5]['data']['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(q[5]['cmd']['interval']))).strftime('%H:%M:%S') for i in range(10)],rotation=0,size='xx-small',)
#             
#             self.axarr[10].set_title('id:6, symbol: %s_%s, interv: %s, price=%.2f, vol=%.2f' % (q[5]['cmd']['symbol'], q[5]['cmd']['type'], q[5]['cmd']['interval'], q[5]['data']['price'][-1], q[5]['data']['vol'][-1]),y=0.85,fontsize='medium') 
#             self.axarr[10].legend(legend1,fontsize='x-small')
#             self.axarr[11].legend(legend2,fontsize='xx-small')
            
                 
        # auto rescale
#         for i in self.axarr:
#             i.relim()
#             i.autoscale_view()

        # We need to draw *and* flush         
        self.figure.canvas.draw()  # will cause isse, Tkinter is intended to be run in a single thread      
        self.figure.canvas.flush_events()
#         print '$$$$$$$$$$$$$$$$$$$$$$ draw done $$$$$$$$'


if __name__ == "__main__":

    # init plot first, instance may be used during cmd handle
    plot = DataPlotter()
    plot.launch()
    
    # init the dict mapping interval to thread of receiver.
    RTDataReceiver = {"1s":None, "5s":None, "10s":None, "30s":None, "1m":None, "5m":None, "10m":None, "30m":None, "1h":None} 

    server = SocketServer.TCPServer(('localhost', 8091), ViewerCmdHandler)
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True  # ctrl+c kill the main thread only. Need put sub-thread in daemon mode so that can be killed by ctrl+c
    t.start()
#     plot.start()
    plot.go()  # need run in main thread,so replace start()


    
