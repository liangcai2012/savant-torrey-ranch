import time
import json
from savant import streamer
import savant.ticker.processors as processors
import savant.ticker
import datetime 

class DataError(RuntimeError):
   def __init__(self, args):
      self.args = args

class DataAPI:
    def __init__(self, clientName):
        self.sc = streamer.getStreamerCaller()
        self.client = clientName 
        self.initialized = False

    def subscribeRealtime(self, symList):
        self.realtime = True
        jret = json.loads(self.sc.subscribe(self.client, symList))
        if jret["response"]["errcode"] == 0:
            self.initialized = True
            return 0
        return -1


    # subscrib a list of tuples [{sym, time}] in this instance for obtaining history, Currently it only return data for the first tuple in the list
    # time format: YYYYMMDD-HHMMSS, this is the start time for history data 
    def subscribeHistory(self, symPeriodList):
        self.realtime = False
        self.symbol = symPeriodList[0]['sym']
        try:
            self.date = symPeriodList[0]['time'].split('-')[0]
            self.current_dt= datetime.datetime.strptime(symPeriodList[0]['time'], '%Y%m%d-%H%M%S')
            #self.start_time= t[0:2]+":"+t[2:4]+":"+t[4:6]+".000"
        except:
            return -1
        
        ticker = processors.TickDataProcessor()
        tickdata = ticker.get_ticks_by_date(self.symbol, self.date, self.date, "full", False, None)
        self.tick_iter = tickdata.iterrows()
        self.tick_batch = []
        return 0

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
            resp = self.sc.update(self.client, interval, ma_mask)
            print resp
            jret = json.loads(resp)
#            jret = json.loads(self.sc.update(self.client, interval, ma_mask))
            print jret
            try:
                if jret["response"]["errcode"] != 0:
                    return None
            except KeyError:
                    return jret["response"]
        else:
            interval_sec = interval_to_int(interval)
            if interval_sec ==-1:
                return None

            while True:
                try:
                    tick = self.tick_iter.next()
                except StopIteration:
                    print "no data"
                    return None 

                time_no_ms = tick[1][0].split('.')[0]# remove the millisecond part
                tick_dt = datetime.datetime.strptime(time_no_ms, '%m/%d/%Y %H:%M:%S')
                if tick_dt < self.current_dt:
                    continue
                if (tick_dt - self.current_dt).seconds < interval_sec:
                    self.tick_batch.append(tick) 
                    continue
                else: #tick_dt >= self.current_dt
                    resp = None
                    if len(self.tick_batch)>0:
                        dt, p_open, p_close, p_high, p_low, volume, p_average = processors.calc_bar_from_tick_batch(self.tick_batch)
                        #timestamp = savant.ticker.datetime_to_timestamp(dt)
                        timestamp = self.current_dt .strftime('%Y%m%d%H%M%S')
                        if timestamp == None:
                            return None
                        resp = {'timestamp': timestamp, "interval": interval, \
                                "data":[{ "symbol":self.symbol, \
                                "bar": str(p_open)+','+str(p_high)+','+str(p_low)+','+str(p_close)+','+str(volume),\
                                "ma": str(p_average)}]}

                    #add the current tick to a new bar
                    while(tick_dt - self.current_dt).seconds >= interval_sec:
                        self.current_dt += datetime.timedelta(0, interval_sec)
                    self.tick_batch=[tick]

                    #return resp if resp is not None otherwise keep going
                    if resp != None:
                        return resp


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
	

def getDataAPI(clientName, serverIP= None, port= None,parameters= None):
	return DataAPI(clientName)
