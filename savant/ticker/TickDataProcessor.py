import os, sys
import pandas, numpy
from datetime import datetime, timedelta

from savant.config import settings


class TickDataProcessor:

    def __init__(self):
        #self.base_dir = settings.DOWNLOAD_DIR
        pass

    def from_file(self, symbol, begin_date, end_date, hours="regular"):
        dates = self.parse_dates(begin_date, end_date)

        if hours == "regular":
            for date in dates:
                data_path = os.path.join(self.base_dir, begin_date, symbol+"_markethours")
        elif hours == "pre":
            for date in dates:
                data_path = os.path.join(self.base_dir, begin_date, symbol+"_premarket")
        elif hours == "after":
            for date in dates:
                data_path = os.path.join(self.base_dir, begin_date, symbol+"_aftermarket")
        else:
            raise ValueError("No such hours: %s" % hours


    def parse_dates(self, begin, end):
        bd = datetime.strptime(begin, "%Y%m%d")
        ed = datetime.strptime(end, "%Y%m%d")
        if bd > ed:
            raise ValueError("Begin date older than end date")
        delta = timedelta(days=1)
        dates = []
        while bd <= ed:
            if bd.weekday() < 5:
                dates.append(bd.strftime("%Y%m%d"))
            bd += delta
        return dates

if __name__ == "__main__":
    ticker = TickDataProcessor()
    print ticker.parse_dates("20140401", "20140407")
    print ticker.parse_dates("20140401", "20140401")
