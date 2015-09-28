import os, sys
import pandas as pd
import numpy
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta

from savant.config import settings
from savant.ticker import calc_time_diff


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
            if not os.path.exists(data_path):
               paths.append("")
            else:
               paths.append(data_path)
        return paths

    def get_ticks_by_date(self, symbol, begin_date, end_date, hours="regular", parse_dates=False, nrows=None):
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
                    print "cannot find", data_path
                    continue
                    #raise IOException("Data file not found: %s" % data_path)
                if parse_dates:
                    dateparse = lambda x: pd.datetime.strptime(x+"000", '%m/%d/%Y %H:%M:%S.%f')
                    cur_ticks = pd.read_csv(data_path, compression="gzip", names=["datetime", "type", "price", "size", "exch", "cond"], parse_dates=[0], date_parser=dateparse, index_col=0, nrows=nrows)
#                    cur_ticks = pd.read_csv(data_path, compression="gzip", names=["datetime", "type", "price", "size", "exch", "cond"], parse_dates=[0], index_col=0, nrows=nrows)
                else:
                    cur_ticks = pd.read_csv(data_path, compression="gzip", names=["datetime", "type", "price", "size", "exch", "cond"], nrows=nrows)
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

def tick2bar(symbol, date, duration=None, interval=1, save_to_disk=False, start_sec_int=None):
    tick_processor = TickDataProcessor()
    ticks = tick_processor.get_ticks_by_date(symbol, date, date)
    begin_time = None
    cur_open_time = None
    tick_batch = []
    bars = pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "average", "volume"])

    for tick in ticks.iterrows():
        time = tick[1][0].split()[1]
        if start_sec_int!=None:
            if int(time.split('.')[0].replace(':','')) < start_sec_int:
                continue
        if cur_open_time == None:
            cur_open_time = time
        if duration != None:
            if begin_time == None:
                begin_time = time
            if calc_time_diff(begin_time, time) > duration:
                return bars

        if calc_time_diff(cur_open_time, time) < interval:
            tick_batch.append(tick)
        else:
            bar = {}
            dt, po, pc, ph, pl, vol, pave = calc_bar_from_tick_batch(tick_batch)
            bar["datetime"]=dt
            bar["open"]=po
            bar["close"]=pc
            bar["high"]=ph
            bar["low"]=pl
            bar["average"]=pave
            bar["volume"]=vol
            bars = bars.append([bar])
            cur_open_time = time
            tick_batch = [tick]
    return bars

def calc_bar_from_tick_batch(ticks):
    dt  = ticks[0][1][0]
    trade_prices= [t[1][2] for t in ticks]
    po = trade_prices[0]
    pc = trade_prices[-1]
    ph = max(trade_prices)
    pl = min(trade_prices)
    vol = sum([int(t[1][3]) for t in ticks])
    trade_cost = sum([t[1][2]*t[1][3] for t in ticks])
    pave = format(trade_cost/vol, ".2f")
    return dt, po, pc, ph, pl, vol, pave 

if __name__ == "__main__":
    #ticker = TickDataProcessor()
    #print ticker.get_ticks_by_date("NTRA", "20150702", "20150702")
    #print ticker.get_ticks_by_datetime("NTRA", datetime.strptime("07/02/2015 11:00:00", "%m/%d/%Y %H:%M:%S"), datetime.strptime("07/02/2015 15:00:00", "%m/%d/%Y %H:%M:%S"))
    print list(tick2bar("NVET", "20150205", 30).iterrows())
