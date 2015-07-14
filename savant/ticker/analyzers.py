import os, sys
import numpy

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
            self.opening = self.tick_data.iloc[0, 3]
        return self.opening

    def get_closing_price(self):
        if not self.closing:
            self.closing = self.tick_data.iloc[-1, 3]
        return self.closing

    def get_first_trade_time(self):
        return self.tick_data.iloc[0, 1]

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

    def validate_input(self):
        try:
            columns = sorted(list(self.tick_data.columns))
            assert sorted(["date", "time", "type", "price", "size", "exch", "cond"]) == columns
        except AssertionError:
            raise Exception("Unexpected columns")


if __name__ == "__main__":
    from savant.ticker.processors import TickDataProcessor
    ticker = TickDataProcessor()
    data = ticker.get_ticks("SERV", "20140626", "20140626")
    analyzer = TradeAnalyzer(data)
    print analyzer.get_opening_price()
    print analyzer.get_closing_price()
    print analyzer.get_first_trade_time()
    print analyzer.get_high_price()
    print analyzer.get_low_price()
    print analyzer.get_high_percent_change()
    print analyzer.get_low_percent_change()
    print analyzer.get_volume()