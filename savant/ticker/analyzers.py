import os, sys
import numpy
import pandas as pd
from datetime import datetime

from savant.config import settings
from savant.ticker import calc_time_diff
# from __builtin__ import None

class TickDataAnalyzer:
    #Class to analyze one-day tick data

    def __init__(self, tick_data):
        self.tick_data = tick_data 

        self.datetime_parsed=False#Chuan: add temp
#         self.validate_input()  #Chuan: comment out
        if self.datetime_parsed:
            self.adj_ind = 1
        else:
            self.adj_ind = 0


        self.open_ind = None
        self.open_vol = None
        self.close_ind = None
        self.close_vol = None

        self.opening = None
        self.closing = None

        self.high = None
        self.low = None
        self.high_percent = None
        self.low_percent = None
        self.volume = None

        self.firstTrVol = None
        self.firstSecVol = None
        self.firstMinVol = None
        self.firstFiveMinVol = None
        self.firstThirtyMinVol = None
        self.firstHourVol = None
        self.firstDayVol = None
        self.firstAfterVol = None

    def get_close_ind(self):
        if not self.close_ind:
            self.close_vol = None
            row_num = len(self.tick_data.index)
            row = row_num 
            following_cond = None
            following_vol = 0

        #if cond 9 proceeds cond15 with same vol, use the cond 9  as the closing
        #if 15 is not proceeded by cond 9, then use the 15 as the closing
        #if cond 15 does not appear in the last 100 record, use the last one as the closing
            for i in range(100):
                row -= 1 
                if row < 0:
                    break
                curr_vol = int(self.tick_data.iloc[row, 3])
                condlist = self.tick_data.iloc[row, 5].split('-')

                # the last record
                if not self.close_vol:
                    self.close_vol = curr_vol 
                    self.close_ind = row

                curr_cond = None
                for cond in condlist:
                    if cond == '9' or cond == '15' or cond == '19':
                        curr_cond = cond
                        break

                if curr_cond == '9' and following_cond == '15' and curr_vol  == following_vol:
                    self.close_vol = curr_vol 
                    self.close_ind = row
                    break
                    
                if following_cond == '15' or following_cond == '19':
                    self.close_vol = following_vol
                    self.close_ind = row +1
                    break

                following_vol = curr_vol
                following_cond = curr_cond


        if row_num - self.close_ind > 5: 
            print "unexpected closing tick at", row_num - self.close_ind 
        return self.open_ind
                
    def get_open_ind(self):
        if not self.open_ind:
            self.open_vol = None
            count = 0
            prev_cond = None
            prev_vol = 0

            for tick in self.tick_data.iterrows():
                if count >= 500:
                    break

                curr_vol = int(tick[1][3])
                condlist = tick[1][5].split('-')

                if not self.open_vol:
                    self.open_vol = curr_vol 
                    self.open_ind = count

                curr_cond = None
                for cond in condlist:
                    if cond == '9' or cond == '17' or cond =='16':
                        curr_cond = cond
                        break

                # in case cond 16 following 9 and vols are identical. It must be the nasdaq opening
                if curr_cond == '16' and prev_cond == '9' and curr_vol  == prev_vol:
                    self.open_vol = curr_vol 
                    self.open_ind = count
                    break
                    

                if (curr_cond =='9' or curr_cond == '17') and curr_vol > self.open_vol: 
                    self.open_vol = curr_vol
                    self.open_ind = count

                prev_vol = curr_vol
                prev_cond = curr_cond
                count += 1    

        return self.open_ind

        

    def get_open_vol(self):
        self.get_open_ind()
        return self.open_vol

    def get_opening_price(self):
        if not self.opening:
            self.get_open_ind()
        self.opening = float(self.tick_data.iloc[self.open_ind, 2-self.adj_ind])
        return self.opening

    def get_closing_price(self):
        if not self.close_ind:
            self.get_close_ind()
        self.closing = float(self.tick_data.iloc[self.close_ind, 2-self.adj_ind])
        return self.closing

    def get_first_trade_time(self):
        self.get_open_ind()
        if self.datetime_parsed:
            return self.tick_data.iloc[self.open_ind].datetime
        else:
            dt = self.tick_data.iloc[self.open_ind, 0].split('.')
            
#            if isinstance(dt, datetime):
#                return self.tick_data.iloc[self.open_ind, 0].strftime("%H:%M:%S")
#            else:
            return datetime.strptime(dt[0], "%m/%d/%Y %H:%M:%S").strftime("%H:%M:%S")
    
    def get_high_price(self):
        if not self.high:
            self.high = max(self.tick_data["price"].tolist()[self.open_ind:])
        return self.high

    def get_low_price(self):
        if not self.low:
            self.low = min(self.tick_data["price"].tolist()[self.open_ind:])
        return self.low

    def get_high_percent_change(self):
        # stock price peak percentage change relative to opening
        if not self.high_percent:
            self.get_high_price()
            self.get_opening_price()
            self.high_percent = float("{:.2f}".format(100*(self.high-self.opening)/self.opening))
        return self.high_percent

    def get_low_percent_change(self):
        # stock price base percentage change relative to opening
        if not self.low_percent:
            self.get_low_price()
            self.get_opening_price()
            self.low_percent = float("{:.2f}".format(100*(self.low-self.opening)/self.opening))
        return self.low_percent 


#the close volume might be replicated. But the value is not very accurage
    def get_volume(self):
        if not self.volume:
            self.volume = int(numpy.sum(self.tick_data["size"].tolist()[self.open_ind:]))
        return self.volume



    #########Analyze volumes from tick data#########################
    def get_first_trade_volume(self):
        if not self.firstTrVol:
            self.firstTrVol = int(self.tick_data.iloc[0]["size"])
        return self.firstTrVol
    def get_first_second_vol(self):
        if not self.firstSecVol:
            t0 = datetime.strptime(self.tick_data.iloc[0]["datetime"],"%m/%d/%Y %H:%M:%S.%f")
            for tick in self.tick_data.iterrows():
#                 print "tick is:" ,tick
                t = datetime.strptime(tick[1]["datetime"],"%m/%d/%Y %H:%M:%S.%f")           
#                 print "t an t0 is:",t, t0
                delta = abs(t-t0).total_seconds()
#                 print "delta is:",delta
                if delta>1:
                    id=tick[0]-1 if tick[0]>0 else 0
                    self.firstSecVol=int(numpy.sum(self.tick_data[0:id]["size"]))
#                     print "vol is:",self.firstSecVol
                    break
        return self.firstSecVol
    
    def get_first_minute_vol(self): 
        if not self.firstMinVol:
            t0 = datetime.strptime(self.tick_data.iloc[0]["datetime"],"%m/%d/%Y %H:%M:%S.%f")
            for tick in self.tick_data.iterrows():
#                 print "tick is:" ,tick
                t = datetime.strptime(tick[1]["datetime"],"%m/%d/%Y %H:%M:%S.%f")           
#                 print "t an t0 is:",t, t0
                delta = abs(t-t0).total_seconds()
#                 print "delta is:",delta
                if delta>60:
                    id=tick[0]-1 if tick[0]>0 else 0
                    self.firstMinVol=int(numpy.sum(self.tick_data[0:id]["size"]))
#                     print "vol is:",self.firstMinVol
                    break
        return self.firstMinVol
    
    def get_first_5m_vol(self):
        if not self.firstFiveMinVol:
            t0 = datetime.strptime(self.tick_data.iloc[0]["datetime"],"%m/%d/%Y %H:%M:%S.%f")
            for tick in self.tick_data.iterrows():
#                 print "tick is:" ,tick
                t = datetime.strptime(tick[1]["datetime"],"%m/%d/%Y %H:%M:%S.%f")           
#                 print "t an t0 is:",t, t0
                delta = abs(t-t0).total_seconds()
#                 print "delta is:",delta
                if delta>300:
                    id=tick[0]-1 if tick[0]>0 else 0
                    self.firstFiveMinVol=int(numpy.sum(self.tick_data[0:id]["size"]))
#                     print "vol is:",self.firstFiveMinVol
                    break
        return self.firstFiveMinVol
     
    def get_first_30m_vol(self):
        if not self.firstThirtyMinVol:
            t0 = datetime.strptime(self.tick_data.iloc[0]["datetime"],"%m/%d/%Y %H:%M:%S.%f")
            for tick in self.tick_data.iterrows():
#                 print "tick is:" ,tick
                t = datetime.strptime(tick[1]["datetime"],"%m/%d/%Y %H:%M:%S.%f")           
#                 print "t an t0 is:",t, t0
                delta = abs(t-t0).total_seconds()
#                 print "delta is:",delta
                if delta>1800:
                    id=tick[0]-1 if tick[0]>0 else 0
                    self.firstThirtyMinVol=int(numpy.sum(self.tick_data[0:id]["size"]))
#                     print "vol is:",self.firstThirtyMinVol
                    break
        return self.firstThirtyMinVol
     
    def get_first_1h_vol(self):
        if not self.firstHourVol:
            t0 = datetime.strptime(self.tick_data.iloc[0]["datetime"],"%m/%d/%Y %H:%M:%S.%f")
            for tick in self.tick_data.iterrows():
#                 print "tick is:" ,tick
                t = datetime.strptime(tick[1]["datetime"],"%m/%d/%Y %H:%M:%S.%f")           
#                 print "t an t0 is:",t, t0
                delta = abs(t-t0).total_seconds()
#                 print "delta is:",delta
                if delta>3600:
                    id=tick[0]-1 if tick[0]>0 else 0
                    self.firstHourVol=int(numpy.sum(self.tick_data[0:id]["size"]))
#                     print "vol is:",self.firstHourVol
                    break
        return self.firstHourVol
     
    def get_first_1d_markethour_vol(self):
        if not self.firstDayVol:
            self.firstDayVol=int(numpy.sum(self.tick_data["size"]))
        return self.firstDayVol
    
    def get_first_1d_aftermarket_vol(self):
        if not self.firstAfterVol:
                self.firstAfterVol=int(numpy.sum(self.tick_data["size"]))
        return self.firstAfterVol
     


    def find_next_spike_by_datetime(self, begin_datetime, noise_level):
        """
        Given a datetime and threshold, return the time, price, and type of the next 
        extremum (major spike or dip) in the tick data. The query datetime cannot
        be earlier than the first trade. 
        :param begin_datetime - datetime
        :param noise_level - threshold
        """
        if not self.datetime_parsed:
            raise TypeError("Datetime not parsed: re-process data with parse_dates flag")
        if not isinstance(begin_datetime, datetime):
            raise ValueError("Invalid datetime value: expected python datetime object")
        t0 = begin_datetime
        p0 = self.get_price_by_datetime(t0)
        if p0 == None:
            raise ValueError("No data available prior to the datetime provided")
        d = 0
        pending = False
        for tick in self.tick_data[begin_datetime:].iterrows():
            t = tick[0]
            p = tick[1][1]
            if not pending:
                if p > p0:
                    d = 1
                elif p < p0:
                    d = -1
                if numpy.absolute(p - p0)/float(p0) > noise_level:
                    pending = True
                    t0 = t
                    p0 = p
            elif d == 1:
                if p > p0:
                    t0 = t
                    p0 = p
                if p < p0 and pending and (p0 - p)/float(p0) > noise_level:
                    pending = False
                    break
            else:
                if p < p0:
                    t0 = t
                    p0 = p
                if pending and p > p0 and (p - p0)/float(p0) > noise_level:
                    pending = False
                    break
        if not pending and d != 0:
            return (t0, p0, d)
        else:
            return None

    def find_next_spike(self, noise_level):
        t0 = self.get_first_trade_time()
        p0 = self.get_opening_price()
        d = 0
        pending = False
        for tick in self.tick_data.iterrows():
            t = tick[0] if self.datetime_parsed else tick[1][0]
            p = float(tick[1][2-self.adj_ind])
            if not pending:
                if p > p0:
                    d = 1
                elif p < p0:
                    d = -1
                if numpy.absolute(p - p0)/p0 > noise_level:
                    pending = True
                    t0 = t
                    p0 = p
            elif d == 1:
                if p > p0:
                    t0 = t
                    p0 = p
                if p < p0 and pending and (p0 - p)/p0 > noise_level:
                    pending = False
                    break
            else:
                if p < p0:
                    t0 = t
                    p0 = p
                if pending and p > p0 and (p - p0)/p0 > noise_level:
                    pending = False
                    break
        if not pending and d != 0:
            return (t0, p0, d)
        else:
            return None


    def get_price_by_datetime(self, dt, tail=False):
        """
        Query the price of the ticker at the datetime provided. If no trade
        occurs at the given datetime, the last trade price retrievable will
        be returned.
        :param dt - datetime
        :param tail - if true function returns the last trade price at the 
                      given datetime
        """
        try:
            rows = self.tick_data.loc[dt]
            if not tail:
                return rows.iloc[0,1]
            else:
                return rows.iloc[-1,1]
        except KeyError:
            data = self.tick_data[:dt]
            if not data.empty:
                return data.iloc[-1, 1]
            else:
                return None

    def validate_data(self):
        try:
            columns = sorted(list(self.tick_data.columns))
            assert sorted(["datetime", "type", "price", "size", "exch", "cond"]) == columns
        except AssertionError:
            raise Exception("Unexpected columns")


class BarDataAnalyzer:
    """
    Class to process and extract useful information from bar data.
    """
    PRICE_TYPES = ("open", "high", "low", "close", "average")

    def __init__(self, data, interval=1):
        self.data = data
        self.interval = interval

    def set_price_type(self, pt):
        if pt not in self.PRICE_TYPES:
            raise ValueError("Unknown price type: must be one of the following (%s)" % ",".join(self.PRICE_TYPES))
        self.price_type = pt
        columns = list(self.data.columns)
        self.price_column = columns.index(self.price_type)  #Chuan: fix self.prcie_type

    def find_spikes(self, noise_level, price_type="open", duration=1000000):
        self.set_price_type(price_type)
        spikes = []
        count = 0
        times = [b[1][0].split()[1] for b in list(self.data.iterrows())]
        t0 = times[0]
        spike = self.find_next_spike(self.data, noise_level)
        if not spike or calc_time_diff(t0, spike[1]) > duration:
            return spikes
        spikes.append([count]+spike[0])
        count += 1
        while calc_time_diff(spike[1], times[-1]) > 0:
            ind = times.index(spike[1])
            spike = self.find_next_spike(self.data[ind+1:], noise_level)
            if spike and calc_time_diff(t0, spike[1]) <= duration:
                spikes.append([count]+spike[0])
                count += 1
            else:
                return spikes

    def find_next_spike(self, bars, noise_level):
        t0 = self.data.iloc[0, 0].split()[1]
        p0 = self.data.iloc[0, self.price_column]
        d = 0
        pending = False
        for row in bars.iterrows():
            t = row[1][0].split()[1]
            p = row[1][self.price_column]
            if not pending:
                if numpy.absolute(p - p0)/p0 > noise_level:
                    pending = True
                    d = 1 if p > p0 else -1
                    t0 = t
                    p0 = p
            elif d == 1:
                if p > p0:
                    t0 = t
                    p0 = p
                if p < p0 and pending and (p0 - p)/p0 > noise_level:
                    pending = False
                    break
            else:
                if p < p0:
                    t0 = t
                    p0 = p
                if pending and p > p0 and (p - p0)/p0 > noise_level:
                    pending = False
                    break
        if not pending and d != 0:
            return [[t0, p0, d], t]
        else:
            return None

    def validate_data(self):
        try:
            columns = sorted(list(self.data.columns))
            assert sorted(["datetime", "open", "high", "low", "close", "average", "volume"]) == columns
        except:
            raise Exception("Unexpected columns: check your data structure")

if __name__ == "__main__":
    from savant.ticker.processors import TickDataProcessor
    ticker = TickDataProcessor()
    data = ticker.get_ticks_by_date("BABA", "20140919", "20140919", parse_dates=False)
#     data = ticker.get_ticks_by_date("FB", "20120518", "20120518", parse_dates=True, nrows=6000)
#    print "1",data
    analyzer = TickDataAnalyzer(data)   #Chuan: change to 'TickDataAnalyzer'
#     print analyzer.get_price_by_datetime(datetime.strptime("07/02/2015 10:43:27.0", "%m/%d/%Y %H:%M:%S"))
#     print analyzer.find_next_spike_by_datetime(datetime.strptime("07/02/2015 10:43:27.0", "%m/%d/%Y %H:%M:%S"), 0.02)
#    print analyzer.get_first_trade_time()
#    print analyzer.get_first_second_vol()
#    print analyzer.get_first_minute_vol()
#    print analyzer.get_first_5m_vol()
#    print analyzer.get_first_30m_vol()
#    print analyzer.get_first_1h_vol()
#    print analyzer.get_first_1d_markethour_vol()
#    print analyzer.get_first_1d_aftermarket_vol()
    print analyzer.get_opening_price()
#     print analyzer.find_next_spike(0.05)
#     print analyzer.tick_data
    
    
#     from savant.ticker.processors import tick2bar
#     bars = tick2bar("NVET", "20150205", 3000)
#     analyzer = BarDataAnalyzer(bars)
#     print analyzer.find_spikes(0.02, price_type="open")
#     print analyzer.find_spikes(0.02, price_type="close")
#     print analyzer.find_spikes(0.02, price_type="average")
