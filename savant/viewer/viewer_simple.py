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
from matplotlib.finance import *
import matplotlib.dates as md
from matplotlib import gridspec

import numpy as np
import savant.dataAPI as dataAPI 
import datetime
import itertools



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
        
        gs = gridspec.GridSpec(3,1)
        self.axarr.append(plt.subplot(gs[:2,-1]))  #subplot1
        self.axarr.append(plt.subplot(gs[2,-1])) 
        plt.setp( self.axarr[0].get_xticklabels(), visible=False)  # invisible vol suplot's x-axes
        
        for i in self.axarr:
            i.grid()      # add grid to all subplots
        
        self.lines=[]
        last_idx=0
        j=0
        marker = itertools.cycle(('b-', 'g-', 'c-', 'm-','y-','k-','co','mo','yo','ko')) 
        axnum = len(self.axarr)/2
        for i in range(10*axnum):
            if i/10>last_idx:    # for every 6 loops, axarr[] idx increase, for exampe: axarr[0],axarr[1] -> axarr[2],axarr[3] 
#                 print i,i/10+j+1,i/10+j+2
                self.lines.append(self.axarr[i/10+j+1].plot([], [], marker.next())[0])
                self.lines.append(self.axarr[i/10+j+2].plot([], [], marker.next())[0])
                j=j+1
            else:
#                 print i,i/10+j,i/10+j+1
                self.lines.append(self.axarr[i/10+j].plot([], [], marker.next())[0])
                self.lines.append(self.axarr[i/10+j+1].plot([], [], marker.next())[0])
            last_idx=i/10
            
    def plotData(self, q, interval):
        
        self.lines[0].set_xdata(q["time"]) 
        self.lines[0].set_ydata(q['price']) 
        self.lines[0].set_label('price_%s' %q["price"])            
        self.lines[1].set_xdata(q["time"])
        self.lines[1].set_ydata(q['vol'])
        self.lines[1].set_label('vol')
        
        i=0  # used for trace the MA type in 'data'
        legend1=[];legend2=[]  #used for dynamic udpate legend

        legend1.append(self.lines[0].get_label()) 
        legend2.append(self.lines[1].get_label()) 
        self.axarr[0].set_ylim(0.9 * min(q['price']), 1.1 * max(q['price']))  # dynamic adj the y limi here!
        self.axarr[1].set_ylim(0, 1.2 * max(q['vol']))
     
        self.axarr[0].set_autoscalex_on(True)   
#       ## set x-axis tick labels, mark label very 10 interval 
        
        #price
        xticks = [matplotlib.dates.num2date(q['time'][0]) + i*10 * datetime.timedelta(0, ConvertInterval(interval)) for i in range(10)]  
        print xticks
        self.axarr[0].set_xticks(xticks)
        #vol
        self.axarr[1].set_xticks(xticks)
        # tick label only show under vol plot
        self.axarr[1].set_xticklabels([xticks[i].strftime('%H:%M:%S') for i in range(len(xticks))])
         
             
        ## set labels
        #self.axarr[0].set_title('id:%s, symbol: %s_%s, interv: %s, price=%.2f, vol=%.2f' % (k,q[k]['cmd']['symbol'], q[k]['cmd']['type'], q[k]['cmd']['interval'], q[k]['data']['price'][-1], q[k]['data']['vol'][-1]),y=0.9)
        self.axarr[0].legend(legend1, fontsize='small')  # auto update legend, in case subplot insertion cause legend number change
        self.axarr[1].legend(legend2, fontsize='x-small')  # in some matplotlib version, we need remove 'handles' name inside legend()
                 
        # auto rescale
        for i in self.axarr:
            i.relim()
            i.autoscale_view()

        plt.show()
        # We need to draw *and* flush         
        #self.figure.canvas.draw()  # will cause isse, Tkinter is intended to be run in a single thread      
        #self.figure.canvas.flush_events()

def fillDataQueue(q, RevData, barType='o'):  
# q[data]= {'time':[20150102-083059],'price':[19.8,19.9,..],'vol':[990,2000,...],'ma':[['20:1700', '19.8:1800'],['19.8:1600', '19.9:1600'],..]}
        xdata = datetime.datetime.strptime(RevData['timestamp'], "%Y%m%d%H%M%S")
        xdata = matplotlib.dates.date2num(xdata)

        symData =RevData['data'][0]
        sym = symData['symbol']
         
        q['time'].append(xdata)
        barSplit = symData['bar'].split(',')
        if barType == 'o':
            barIndex = 0
        elif barType == 'h':
            barIndex = 1
        elif barType == 'l':
            barIndex = 2
        elif barType == 'c':
            barIndex = 3
        else:
            print 'invalid bar type'
            exit()
        q['price'].append(float(barSplit[barIndex]))
        q['vol'].append(float(barSplit[4]))
            

if __name__ == "__main__":

    # init plot first, instance may be used during cmd handle
    plot = DataPlotter()
    plot.launch()

    da = dataAPI.getDataAPI("viewer_simple")
    q = {"time":[], "price": [], "vol": []} 
    if da.subscribeHistory([{"sym":"NTRA", "time":"20150702-090000"}]) != 0:
        print "fail to subscribe"
        exit()
    while True:
        ret = da.update("10s")
        if ret == None:
            break
        fillDataQueue(q, ret) 
        interval = ret["interval"]
    print "data filled: ", len(q["time"]), len(q["price"]), len(q["vol"])
    plot.plotData(q, interval)  # need run in main thread,so replace start()


    
