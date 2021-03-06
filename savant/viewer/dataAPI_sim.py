from json import loads,dumps 
import time
import datetime 
import random
import matplotlib

class DataError(RuntimeError):
   def __init__(self, args):
      self.args = args

class DataAPI:

    #cound is a static variable and used to generate a unique name for each Data instance to access streamer. 
    #the unique name shall be clientName+'_'+str(count), where clientName is specified in __init__ method.     
    count=0



    # initialiazation for getting real time or historical data interface.
    # if no serverIPaddress or port is specified then this inteface instance 
    #is for history data. Otherwise it is for streaming data

    # generates a DataError exception if it fails to connect to the streamer server.
    def __init__(self, clientName, serverIP= None, port= None,parameters= None):
#         raise NotImplementedError("Subclass must implement abstract method")
        self.price1_h_last=200
        self.price1_l_last=180
        self.price1_o_last=190
        self.price1_c_last=195
        self.vol_last=20000
        
    # subscribe a list of symbals in this interface instance for obtaining realtime.
    # raise an error if serverIp or port is not specified in __init__ 
    def subscribeRealtime(self, symList):
#             raise NotImplementedError("Subclass must implement abstract method")
        pass
    # subscrib a list of tuples [{sym, time}] in this instance for obtaining history.
    # time format: YYYYMMDD-HHMMSS
    # raise an error if serverIp and port are specified in __init__
    # read multiple history data in one instance is not common. In most case the list 
    # should contain only one sym-time tuple. 
    def subscribeHistory(self, symPeriodList):
#             raise NotImplementedError("Subclass must implement abstract method")
        pass

    # unsubscribe part of symbols previous subscribed 
    def unsubscribeRealtime(self, symList):
#             raise NotImplementedError("Subclass must implement abstract method")
        print '###############unsubscribed realtime!!!!!!!!!!!!!!'

    # unsubscribe part of the symbol-time tuples previous subscribed. For history data, this api has no real effect
    def unsubscribeHistory(self, symPeriodList):
#             raise NotImplementedError("Subclass must implement abstract method")
        print '###############unsubscribed realtime!!!!!!!!!!!!!!'

    # update data with given interval
    # return a list of data for all subscribed symbol or symbol-time tuples. The returned data format can be seen in 
    def update(self, interval, bar_mask, ma_mask):
#         raise NotImplementedError("Subclass must implement abstract method")
        now=time.time()
        st = datetime.datetime.fromtimestamp(now)#.strftime('%Y-%m-%d %H:%M:%S')
        
        self.price1_h_new=random.uniform(self.price1_h_last*0.9,self.price1_h_last*1.1)
        self.price1_h_last=self.price1_h_new
        self.price1_l_new=random.uniform(self.price1_l_last*0.9,self.price1_l_last*1.1)
        self.price1_l_last=self.price1_l_new
        self.price1_o_new=random.uniform(self.price1_o_last*0.9,self.price1_o_last*1.1)
        self.price1_o_last=self.price1_o_new
        self.price1_c_new=random.uniform(self.price1_c_last*0.9,self.price1_c_last*1.1)
        self.price1_c_last=self.price1_c_new
        self.vol_new=random.uniform(self.vol_last*0.95,self.vol_last*1.05)
        self.vol_last=self.vol_new
        data=dumps({'client':'viewer_1s','timestamp':matplotlib.dates.date2num(st),'data':[{'symbol':'QQQ','bar':{'h':self.price1_h_new,'l':self.price1_l_new, 'o':self.price1_o_new,'c':self.price1_c_new, 'vol':self.vol_new},'ma':[ None,None ,None ,None ,'190:20000','201:21000', None,None ,None ],'delay':'1s'}]})
#         data=dumps({'client':'viewer_1s','timestamp':matplotlib.dates.date2num(st),'data':[{'symbol':'QQQ','bar':{'h':self.price1_h_new,'l':self.price1_l_new, 'vol':self.vol_new},'ma':{'1m':'190:20000','5m':'201:21000'},'delay':'1s'}]})
        return data

#    def setReponseMsg(self, client, symbol, bar, ma, delay, timestamp, interval):
#        data = {"symbol": symbol,\
#                "bar": bar, \
#                "ma": ma,\
#                  "delay" :delay}
#        msg = {"client": client, "timestamp": timestamp ,\
#               "interval": interval,
#               "data":data
#               }
#        return msg


if __name__ == "__main__":
    print("ok")
    print("ok")
