import os, sys
import pandas as pd
import numpy
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta

from savant.config import settings


class TickDataProcessor:
    BATCH_SIZE = 10000

    def __init__(self):
        self.base_dir = settings.DOWNLOAD_DIR

    def get_ticks_paths_by_date(self, symbol, date):
        paths=[]
        suffix_list = self.get_file_suffix("full")
        for suffix in suffix_list:
            filename = symbol + suffix + ".csv.gz" 
            data_path = os.path.join(self.base_dir, date, filename)
            print data_path
            if not os.path.exists(data_path):
               paths.append("")
            else:
               paths.append(data_path)
        return paths

    def get_ticks_by_date(self, symbol, begin_date, end_date, hours="regular", parse_dates=False, nr = None):
        dates = self.parse_dates(begin_date, end_date)

        suffix = self.get_file_suffix(hours)
        filenames = [symbol + s + ".csv.gz" for s in suffix]

        if parse_dates:
            tick_data = pd.DataFrame(columns=["type", "price", "size", "exch", "cond"])
        else:
            tick_data = pd.DataFrame(columns=["datetime", "type", "price", "size", "exch", "cond"])

        for date in dates:
            for filename in filenames:
                data_path = os.path.join(self.base_dir, date, filename)
                if not os.path.exists(data_path):
                    raise IOException("Data file not found: %s" % data_path)
                if parse_dates:
                    cur_ticks = pd.read_csv(data_path, compression="gzip", names=["datetime", "type", "price", "size", "exch", "cond"], parse_dates=[0], index_col=0)
                else:
                    cur_ticks = pd.read_csv(data_path, compression="gzip", names=["datetime", "type", "price", "size", "exch", "cond"], nrows = nr)
                tick_data = tick_data.append(cur_ticks)
        return tick_data

    def get_ticks_by_datetime(self, symbol, begin_datetime, end_datetime, hours="regular", parse_dates=False):
        if not isinstance(begin_datetime, datetime) or not isinstance(end_datetime, datetime):
            raise ValueError("Invalid datetime")

        tick_data = self.get_ticks_by_date(symbol, begin_datetime.strftime("%Y%m%d"), end_datetime.strftime("%Y%m%d"), hours=hours, parse_dates=True)
        return tick_data[begin_datetime:end_datetime] 

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

    def get_file_suffix(self, hours):
        if hours == "regular":
            suffix = ["_markethours"]
        elif hours == "pre":
            suffix = ["_premarket"]
        elif hours == "after":
            suffix = ["_aftermarket"]
        elif hours == "full":
            suffix = ["_markethours", "_premarket", "_aftermarket"]
        else:
            raise ValueError("No such hours: %s" % hours)
        return suffix


if __name__ == "__main__":
    ticker = TickDataProcessor()
    print ticker.get_ticks_by_date("NTRA", "20150702", "20150702")
    print ticker.get_ticks_by_datetime("NTRA", datetime.strptime("07/02/2015 11:00:00", "%m/%d/%Y %H:%M:%S"), datetime.strptime("07/02/2015 15:00:00", "%m/%d/%Y %H:%M:%S"))
