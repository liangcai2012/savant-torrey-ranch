import os, sys
import numpy
from datetime import datetime

from savant.config import settings

class TradeAnalyzer:
    """
    Class to analyze one-day tick data
    """

    def __init__(self, tick_data):
        self.tick_data = tick_data
        self.validate_input()
        self.opening = None
        self.closing = None
        self.high = None
        self.low = None
        self.high_percent = None
        self.low_percent = None
        self.volume = None

    def get_opening_price(self):
        if not self.opening:
            self.opening = self.tick_data.iloc[0, 2]
        return self.opening

    def get_closing_price(self):
        if not self.closing:
            self.closing = self.tick_data.iloc[-1, 2]
        return self.closing

    def get_first_trade_time(self):
        dt = self.tick_data.iloc[0, 0]
        if isinstance(dt, datetime):
            return self.tick_data.iloc[0, 0].strftime("%H:%M:%S")
        else:
            return datetime.strptime(dt, "%m/%d/%Y %H:%M:%S").strftime("%H:%M:%S")

    def get_high_price(self):
        if not self.high:
            self.high = self.tick_data["price"].max()
        return self.high

    def get_low_price(self):
        if not self.low:
            self.low = self.tick_data["price"].min()
        return self.low

    def get_high_percent_change(self):
        # stock price peak percentage change relative to opening
        if not self.high_percent:
            opening = self.get_opening_price()
            high = self.get_high_price()
            self.high_percent = 100*(high-opening)/float(opening)
        return self.high_percent

    def get_low_percent_change(self):
        # stock price base percentage change relative to opening
        if not self.low_percent:
            opening = self.get_opening_price()
            low = self.get_low_price()
            self.low_percent = 100*(low-opening)/float(opening)
        return self.low_percent 

    def get_volume(self):
        if not self.volume:
            self.volume = int(numpy.sum(self.tick_data["size"]))
        return self.volume

    def find_next_spike(begin_datetime, noise_level):
        if not isinstance(begin_datetime, datetime):
            raise ValueError("Invalid datetime value: expected python datetime object")
        t0 = begin_datetime
        p0 = self.get_price_by_datetime(t)
            
                
    def get_price_by_datetime(self, dt):
        data = self.tick_data[:dt]
        if not data.empty:
            return data.iloc[-1, 2]
        else:
            return None

    def validate_input(self):
        try:
            columns = sorted(list(self.tick_data.columns))
            assert sorted(["datetime", "type", "price", "size", "exch", "cond"]) == columns
        except AssertionError:
            try:
                assert sorted(["type", "price", "size", "exch", "cond"]) == columns
            except AssertionError:
                raise Exception("Unexpected columns")


if __name__ == "__main__":
    from savant.ticker.processors import TickDataProcessor
    ticker = TickDataProcessor()
    data = ticker.get_ticks_by_date("NTRA", "20150702", "20150702", parse_dates=True)
    analyzer = TradeAnalyzer(data)
    print analyzer.get_price_by_datetime(datetime.strptime("07/02/2015 11:00:00", "%m/%d/%Y %H:%M:%S"))
