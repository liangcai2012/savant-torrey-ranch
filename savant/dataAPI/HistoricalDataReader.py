import helper
import dataAPI
import os
import datetime
import time
class CBarData:
    def __init__(self):
        self.SummaryOfPrice = 0
        self.open = 0;
        self.close = 0
        self.high = 0;
        self.low= 0
        self.volume=0
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
        ret = {"open":self.open, "close":self.close, \
               "low":self.low, "high":self.high, \
               "volume":self.volume,"avg": self.avg}

        return ret


class HistoricalDataReader:
    def __init__(self, symbol, startDay, endDay):
        self.bardata = CBarData()
        self.symbol = symbol
        self.startDay = startDay
        self.endDay = endDay
        filepath = helper.GetDataFileFullPath(symbol,startDay)
        self.dataFile = open(filepath, "r+");
        self.lastDataLine = None
        self.processedCount = 0;
        self.updateCount = 0
    def ParseTradeData(self, loopCount, line):
        fields = line.split("\t")
        fields_time =  fields[0].split("[")
        fields2_time =  fields_time[2].split("]")
        t1 = datetime.datetime.strptime(fields2_time[0], "%m/%d/%Y %H:%M:%S")
        timestamp = time.mktime(t1.timetuple())
        fields_last = fields[1].split(":")
        fields_lastsize = fields[2].split(":")
        self.process(loopCount, timestamp, fields_last[1], fields_lastsize[1])
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
    # Paramters bar_mask, ma_mask are ignored.
    # todo support using Paramters bar_mask, ma_mask .
    def update(self, interval, bar_mask, ma_mask):
        self.updateCount +=1
        loopCount = 0
        self.interval = interval
        self.hasMoreData = True
        while True:

            if self.lastDataLine == None:
                self.lastDataLine = self.dataFile.readline()
            if not self.lastDataLine:
                # raise exception only loopCount ==0.
                # loopCount !=0 means partial data.
                if(loopCount ==0):
                     raise dataAPI.DataError([-1,"End of data"])

                print("end of data")
                break
            #if(loopCount == 657):
             #   print(self.lastDataLine)
            self.ParseTradeData(loopCount, self.lastDataLine)

            self.processedCount+=1
            loopCount+=1
            if self.hasMoreData == False:
                print(self.updateCount, "end of current period")
                break
            self.lastDataLine = None
        return self.bardata.toDictionary()

if __name__ == "__main__":
    hdr = HistoricalDataReader("qqq", "05/01/2015", "05/01/2015")
    for i in range(3600 *9):
        try:
            ret = hdr.update(1,"000000", "000000")
            print(ret)
        except dataAPI.DataError, e:
            print("total available number of bar data:", i)
            break

    print("done")