import os, sys
import numpy
from datetime import datetime

from savant.config import settings
from savant.ticker import calc_time_diff

class TickDataAnalyzer:
    """
    Class to analyze one-day tick data
    """

    def __init__(self, tick_data):
        self.tick_data = tick_data
        self.validate_input()
        if self.datetime_parsed:
            self.adj_ind = 1
        else:
            self.adj_ind = 0
        self.opening = None
        self.closing = None
        self.high = None
        self.low = None
        self.high_percent = None
        self.low_percent = None
        self.volume = None

    def get_opening_price(self):
        if not self.opening:
            self.opening = self.tick_data.iloc[0, 2-self.adj_ind]
        return float(self.opening)

    def get_closing_price(self):
        if not self.closing:
            self.closing = self.tick_data.iloc[-1, 2-self.adj_ind]
        return float(self.closing)

    def get_first_trade_time(self):
        if self.datetime_parsed:
            return self.tick_data.iloc[0].name
        else:
            dt = self.tick_data.iloc[0, 0]
            if isinstance(dt, datetime):
                return self.tick_data.iloc[0, 0].strftime("%H:%M:%S")
            else:
                return datetime.strptime(dt, "%m/%d/%Y %H:%M:%S").strftime("%H:%M:%S")

    def get_high_price(self):
        if not self.high:
            self.high = self.tick_data["price"].max()
        return float(self.high)

    def get_low_price(self):
        if not self.low:
            self.low = self.tick_data["price"].min()
        return float(self.low)

    def get_high_percent_change(self):
        # stock price peak percentage change relative to opening
        if not self.high_percent:
            opening = self.get_opening_price()
            high = self.get_high_price()
            self.high_percent = 100*(high-opening)/opening
        return self.high_percent

    def get_low_percent_change(self):
        # stock price base percentage change relative to opening
        if not self.low_percent:
            opening = self.get_opening_price()
            low = self.get_low_price()
            self.low_percent = 100*(low-opening)/opening
        return self.low_percent 

    def get_volume(self):
        if not self.volume:
            self.volume = int(numpy.sum(self.tick_data["size"]))
        return self.volume

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

    def find_spikes(self, noise_level, price_type="open", duration=1000000):
        if price_type not in self.PRICE_TYPES:
            raise ValueError("Unknown price type: must be one of the following (%s)" % ",".join(self.PRICE_TYPES))
        spikes = []
        count = 0
        times = [b[1][0].split()[1] for b in list(self.data.iterrows())]
        spike = self.find_next_spike(self.data, noise_level)
        if not spike:
            return spikes
        spikes.append(spike)
        while spike[0] < times[-1]:
            if calc_time_diff(t0, time) > duration:
                return spikes
            ind = times.index(spike[0])
            bars = self.data[ind+1:]
            spike = self.find_next_spike(bars, noise_level)
            if spike:
                spikes.append(spike)
            else:
                return spikes

    def find_next_spike(self, bars, noise_level):
        t0 = self.data.iloc[0, 0].split()[1]
        p0 = self.data.iloc[0, self.price_column]
        d = 0
        pending = False
        for row in bars.iterrows():
            t = row[1][0]
            p = row[1][self.price_column]
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

    def set_price_column(self, price_type):
        columns = list(self.data.columns)
        return columns.index(price_type)

    def validate_data(self):
        try:
            columns = sorted(list(self.data.columns))
            assert sorted(["datetime", "open", "high", "low", "close", "average", "volume"]) == columns
        except:
            raise Exception("Unexpected columns: check your data structure")

if __name__ == "__main__":
    #from savant.ticker.processors import TickDataProcessor
    #ticker = TickDataProcessor()
    #data = ticker.get_ticks_by_date("FB", "20120518", "20120518", parse_dates=False)
    #data = ticker.get_ticks_by_date("FB", "20120518", "20120518", parse_dates=True, nrows=6000)
    #analyzer = TradeAnalyzer(data)
    #print analyzer.get_price_by_datetime(datetime.strptime("07/02/2015 10:43:27", "%m/%d/%Y %H:%M:%S"))
    #print analyzer.find_next_spike_by_datetime(datetime.strptime("07/02/2015 10:43:27", "%m/%d/%Y %H:%M:%S"), 0.02)
    #print analyzer.get_first_trade_time()
    #print analyzer.get_opening_price()
    #print analyzer.find_next_spike(0.05)
    #print analyzer.tick_data
    from savant.ticker.processors import tick2bar
    bars = tick2bar("NVET", "20150205", 30)
    analyzer = BarDataAnalyzer(bars)
    analyzer.find_spikes()
