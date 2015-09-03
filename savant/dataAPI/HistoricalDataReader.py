import helper
import errors
import dataAPI
import os
import datetime
import time
import readgz
import matplotlib.dates

class CBarData:
    def __init__(self):
        self.reset()
    def reset(self):
        self.SummaryOfPrice = 0
        self.open = 0;
        self.close = 0
        self.high = 0;
        self.low= 0
        self.volume=0
        self.avg =0
    def Process(self, loopCount, lastPrice, lastSize):
            if loopCount == 0:
                self.open = lastPrice
                self.close = lastPrice
                self.low = lastPrice
                self.high = lastPrice;
                self.volume = lastSize
                self.SummaryOfPrice = lastPrice
            else:
                if(lastPrice < self.low):
                    self.low = lastPrice
                if(lastPrice > self.high):
                    self.high = lastPrice
                self.SummaryOfPrice += lastPrice
                self.volume += lastSize
            self.close = lastPrice
    def Done(self, loopCount):
            self.avg = self.SummaryOfPrice / (loopCount)
            # round up to two decimal digits
            self.avg =int((self.avg * 100) + 0.5) / 100.0 # Adding 0.5 rounds it up
            #self.avg = "%.2f" % self.avg

    def toDictionary(self):   
        ret = {"error":None,\
            "data":[{ "symbol":None,
            "bar":{ "open":self.open, "close":self.close, \
               "low":self.low, "high":self.high,
               "volume":self.volume,"avg": self.avg}, 
              "ma":None}      
                    ] }          # Chuan: change API for compatible with viewer

        return ret



class HistoricalDataReader:
    def __init__(self, symbol, startDay, endDay):
        self.bardata = CBarData()
        self.symbol = symbol
        self.startDay = startDay
        self.endDay = endDay
        self.lastError=errors.EC_NOT_ERROR
        self.startTimestamp = None

        filepath = helper.GetDataFileFullPath(symbol,startDay)
        try:
            #self.dataFile = open(filepath, "r+");
            self.dataFile  = readgz.Reader_gz()
            self.dataFile.open(filepath)
        except:
            self.dataFile = None
            self.lastError=errors.EC_File_not_exist

        self.lastDataLine = None
        self.processedCount = 0;
         # the number of time update function is called.
        self.updateCount = 0
    def ParseTradeData(self, loopCount, line):
        fields = line.split(",")
        #fields_time =  fields[0].split("[")
        fields2_time =  fields[0] #.split("]")
        t1 = datetime.datetime.strptime(fields2_time, "%m/%d/%Y %H:%M:%S.%f")
        timestamp = time.mktime(t1.timetuple())
        fields_last = fields[2]
        fields_lastsize = fields[3]
        self.process(loopCount, timestamp, fields_last, fields_lastsize)
    def process(self,loopCount, timestamp, lastPrice, lastSize ):
        if loopCount == 0:
                self.startTimestamp = timestamp
        if timestamp - self.startTimestamp < (self.interval):
            lprice = float(lastPrice)
            lSize = float(lastSize)
            self.bardata.Process(loopCount, lprice, lSize)
            self.hasMoreData = True
        else:
            self.bardata.Done(loopCount)
            self.hasMoreData = False
    def read_and_process_data(self):
        loopCount = 0
        if(self.dataFile == None):
            #do nothing if data file object is not available.
            return
        while True:

            if self.lastDataLine == None:
                self.lastDataLine = self.dataFile.readline()
            if not self.lastDataLine:
                # raise exception only loopCount ==0.
                # loopCount !=0 means partial data.
                if(loopCount ==0):
                    #raise dataAPI.DataError([-1,"End of data"])
                    #self.dataFile.close()
                    self.lastError = errors.EC_END_OF_DATA
                    self.dataFile = None

                print("end of data")
                break
            #if(loopCount == 657):
             #   print(self.lastDataLine)
            self.ParseTradeData(loopCount, self.lastDataLine)

            self.processedCount+=1
            loopCount+=1
            if self.hasMoreData == False:
                #print(self.updateCount, "end of current period")
                break
            self.lastDataLine = None
    # Paramters bar_mask, ma_mask are ignored.
    # todo support using Paramters bar_mask, ma_mask .
    def update(self, interval, bar_mask, ma_mask):
        self.updateCount +=1
        loopCount = 0
        self.interval = interval
        self.hasMoreData = True
        if self.dataFile == None:
            if(self.startTimestamp != None):
                self.startTimestamp +=interval
            self.bardata.reset()
            ret = self.bardata.toDictionary()
            if self.lastError == 0:
                ret["error"] = None
            else:
                ret["error"] = errors.errors[self.lastError]
        else:
            self.read_and_process_data()
            ret = self.bardata.toDictionary()
        #self.startTimestamp
        tstr = self.get_timestamp()
        ret["time_stamp"] =  tstr
        ret["data"][0]["symbol"]=self.symbol  # Chuan: change API for compatible with viewer
        return ret
    def get_timestamp(self):

        # data is not available
        if(self.startTimestamp == None):
            #just use the date specified in update function.
           ret = self.startDay
           #self.updateCount
        else:
            adjust_time = 8 *3600; #8 hours
            t = datetime.datetime.utcfromtimestamp(self.startTimestamp - adjust_time)
#             ret = t.strftime("%Y-%m-%d %H:%M:%S")
            ret=t
            print ret
        return matplotlib.dates.date2num(ret) # Chuan: change timestamp to float, viwer will do the convertion


if __name__ == "__main__":
    o = CBarData()
    o.toDictionary()
    hdr = HistoricalDataReader("BTER", "/2015/08/05", "2015/08/06")
    for i in range(3600 *9):
        try:
            #for i in range(10):
            ret = hdr.update(1,"000000", "000000")
            errorObj = ret["error"]
            print(ret)
            if(errorObj != None):
                break;
        except dataAPI.DataError, e:
            print("total available number of bar data:", i)
            break

    print("done")
