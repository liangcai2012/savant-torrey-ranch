import time
import json
import sys
sys.path.append("../../")
from savant import streamer
print sys.path

class DataError(RuntimeError):
   def __init__(self, args):
      self.args = args

class DataAPI:
    def __init__(self, clientName, serverIP= None, port= None,parameters= None):
        self.sc = streamer.getStreamerCaller()
        self.client = clientName 
        if severIP != None:
            self.realtime = True
        self.realtime = Fales



    def subscribeRealtime(self, symList):
        if self.realtime:
            jret = json.loads(self.sc.subscribe(self.client, symList))
            if jret["response"]["errcode"] == 0:
                return 0
        return -1


    # subscrib a list of tuples [{sym, time}] in this instance for obtaining history.
    # time format: YYYYMMDD-HHMMSS
    # raise an error if serverIp and port are specified in __init__
    # read multiple history data in one instance is not common. In most case the list 
    # should contain only one sym-time tuple. 
    def subscribeHistory(self, symPeriodList):
        pass


    # unsubscribe part of symbols previous subscribed 
    def unsubscribeRealtime(self):
        if self.realtime:
            jret = json.loads(self.sc.unsubscribe(self.client))
            if jret["response"]["errcode"] == 0:
                return 0
        return -1

    # unsubscribe part of the symbol-time tuples previous subscribed. For history data, this api has no real effect
    def unsubscribeHistory(self, symPeriodList):
        pass


    # update data with given interval
    # return a list of data for all subscribed symbol or symbol-time tuples. The returned data format can be seen in 
    def update(self, interval, bar_mask, ma_mask):
        if self.realtime:
            return json.loads(self.sc.unsubscribe(self.client))


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
