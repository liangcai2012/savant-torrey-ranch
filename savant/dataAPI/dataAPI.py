import time
import json
from savant import streamer
import savant.ticker.processors as processors
import savant.ticker

class DataError(RuntimeError):
   def __init__(self, args):
      self.args = args

class DataAPI:
    def __init__(self, clientName, serverIP= None, port= None,parameters= None):
        self.sc = streamer.getStreamerCaller()
        self.client = clientName 
        if serverIP != None:
            self.realtime = True
        self.realtime = False
        self.initialized = False

    def subscribeRealtime(self, symList):
        if self.realtime:
            jret = json.loads(self.sc.subscribe(self.client, symList))
            if jret["response"]["errcode"] == 0:
                self.initialized = True
                return 0
        return -1


    # subscrib a list of tuples [{sym, time}] in this instance for obtaining history, Currently it only return data for the first tuple in the list
    # time format: YYYYMMDD-HHMMSS, this is the start time for history data 
    def subscribeHistory(self, symPeriodList):
        if self.realtime:
           return -1
        self.symbol = symPeriodList[0]['sym']
        try:
            [d, t] = symPeriodList[0]['time'].split('-')
            self.start_time= t[0:2]+":"+t[2:4]+":"+t[4:6]+".000"
            self.date = d
        except:
            return -1
        
        ticker = processors.TickDataProcessor()
        tickdata = ticker.get_ticks_by_date(self.symbol, self.date, self.date, "full", False, None)
        self.tick_iter = tickdata.iterrows()
        self.tick_batch = []
        try:
            while True:
                tick = self.tick_iter.next()
                time = tick[1][0].split()[1]
                if savant.ticker.calc_time_diff(self.start_time, time) < 0:
                    continue
                else:
                    self.tick_batch.append(tick)
                    self.current_time = time
                    self.initialized = True
                    return 0
        except StopIteration:
            print "Cannot not find ticks after start time", t
            return -1

    # unsubscribe all symbols previous subscribed symbosl 
    def unsubscribe(self):
        self.initialized = False
        if self.realtime:
            jret = json.loads(self.sc.unsubscribe(self.client))
            if jret["response"]["errcode"] == 0:
                return 0
        return -1

    # update data with given interval
    # return a list of data for all subscribed symbol or symbol-time tuples. The returned data format can be seen in 
    def update(self, interval, bar_maski="11111", ma_mask="111111111"):
        if self.realtime:
            jret = json.loads(self.sc.update(self.client, interval, ma_mask))
            if jret["response"]["errcode"] != 0:
                return None
            return jret["response"]
        else:
            interval_sec = interval_to_int(interval)
            if interval_sec ==-1:
                return None

            while True:
                try:
                    tick = self.tick_iter.next()
                except StopIteration:
                    return None 

                time = tick[1][0].split()[1]
                if savant.ticker.calc_time_diff(self.current_time, time) < interval_sec:
                    self.tick_batch.append(tick) 
                    continue
                else:
                    timestamp = savant.ticker.datetime_to_timestamp(self.tick_batch[0][1][0])
                    if timestamp == None:
                        return None
                    #there is at least one tick in self.tick_batch
                    trade_cost= [t[1][2]*t[1][3] for t in self.tick_batch]
                    p_open = trade_prices[0]
                    p_close = trade_prices[-1]
                    p_high = max(trade_prices)
                    p_low = min(trade_prices)
                    volume = sum([int(t[1][3]) for t in self.tick_batch])
                    p_average = sum(trade_cost)/float(volume)
                    resp = {'timestamp': timestamp, "interverl": interval, \
                            "data":[{ "symbol":self.symbol, \
                            "bar": '"'+str(p_open)+','+str(p_high)+','+str(p_low)+','+str(p_close)+','+str(volume)+'"',\
                            "ma": '"'+ str(p_average)+ '"'}]}
                    self.tick_batch=[tick]
                    break


def interval_to_int(interval):
    if interval == '1s':
        return 1
    elif interval == "5s":
        return 5
    elif interval == "10s":
        return 10
    elif interval == "30s":
        return 30
    elif interval == "1m":
        return 60
    elif interval == "5m":
        return 300
    elif interval == "10m":
        return 600
    elif interval == "30m":
        return 1800
    elif interval == "1h":
        return 3600
    else:
        return -1


if __name__ == "__main__":

    da = DataAPI("test")
    if da.subscribeHistory([{"sym":"NTRA", "time":"20150702-090000"}]) != 0:
        print "fail to unsubscribe"
        exit()
    while True:
        ret = da.update("1s")
        print ret
        if ret == None:
            break
