import os, sys
import pandas as pd
import numpy
import subprocess
from collections import defaultdict
import datetime
import subprocess

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
                    continue
                    #print "cannot find", data_path
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
        bd = datetime.datetime.strptime(begin, "%Y%m%d")
        ed = datetime.datetime.strptime(end, "%Y%m%d")
        if bd > ed:
            raise ValueError("Begin date older than end date")
        delta = datetime.timedelta(days=1)
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
            suffix = ["_premarket", "_markethours", "_aftermarket"]
        else:
            raise ValueError("No such hours: %s" % hours)
        return suffix

# scope must be "full" or "regular"
# date must be in form of "YYYYMMDD"
# time must be in form of "HHMMSS" if not None

# get_next_bar returns date, o/h/l/c/v, average 
def Tick2SecondBarConverter(symbol, date):
    bar_path = settings.DATA_HOME+ '/data/' + date + '/' +symbol+"_second_bar.csv" 
    bar_gz_path = bar_path+".gz" 
    if os.path.exists(bar_gz_path):
        print "secondly bar file already exists"
        return

    try:
        fbar = open(bar_path, 'w')
    except IOError:
        print "Cannot open ", bar_path
        return

    ticker = TickDataProcessor()
    tickdata = ticker.get_ticks_by_date(symbol, date, date, "full", False, None)
    tick_iter = tickdata.iterrows()
    begin_time = None
    tick_batch = []
    current_dt = None

    cond_9= False
    cond_15 = False
    while True:
        try:
            tick = tick_iter.next()
        except StopIteration:
            fbar.close()
            #print "gzipping", bar_path
            subprocess.check_call(["gzip", bar_path])
            return 



        #handle conditions
        #assumption: conditions cannot contain both 9 and 15 or 16
        #9 might be followed by 15 or 16
        #any record before 16 is not valid

        condlist = tick[1][5].split('-')
        for cond in condlist:
            if cond == '9' or cond == "15" or cond == "16":
                break
        if cond == '9':
            cond_9 = True 
            prev_vol = int(tick[1][3]) 
        elif cond == '16':
            if cond_9 and int(tick[1][3]) == prev_vol:
# do not remove the second bars before open, try to be literate as the tick data
#                if len(tick_batch)>1:
#                    print symbol, date, "contains trade records before offical open!"
#                tick_batch=[]
                cond_9 = False
                continue
        elif cond == "15":
            if cond_9 and int(tick[1][3]) == prev_vol:
                cond_9 = False
                continue
        else:
            if cond_9:
                cond_9 = False

        time_no_ms = tick[1][0].split('.')[0]# remove the millisecond part
        tick_dt = datetime.datetime.strptime(time_no_ms, '%m/%d/%Y %H:%M:%S')
        if current_dt == None:
            current_dt = tick_dt
        if (tick_dt - current_dt).seconds < 1:
            tick_batch.append(tick) 
            continue
        else: #tick_dt >= self.current_dt
            if len(tick_batch)>0:
                p_open, p_close, p_high, p_low, volume, p_average = calc_bar_from_tick_batch(tick_batch)
                if p_open != None:
                    fbar.write(current_dt.strftime("%Y%m%d%H%M%S") + ", " + str(p_open) + ", " + str(p_high) + ", "+ str(p_low) + ", " + str(p_close) + ", " + str(volume) + ", " + p_average + '\n')

            while(tick_dt - current_dt).seconds >= 1:
                current_dt += datetime.timedelta(0, 1)
            tick_batch=[tick]


def calc_bar_from_tick_batch(ticks):
    trade_prices= [t[1][2] for t in ticks]
    po = trade_prices[0]
    pc = trade_prices[-1]
    ph = max(trade_prices)
    pl = min(trade_prices)
    vol = sum([int(t[1][3]) for t in ticks])
    #there are chances that tick record with vol = 0
    if vol == 0:
        return None, None, None, None, None, None
    trade_cost = sum([t[1][2]*t[1][3] for t in ticks])
    pave = format(trade_cost/vol, ".2f")
    return po, pc, ph, pl, vol, pave 



#TODO: This function needs to be re-written 
def tick2bar(symbol, date, duration=None, interval=1, save_to_disk=False, start_sec_int=None):
    scope = "full"
    start_time = None
    if start_sec_int != None:
        if start_sec_int >= 93000:
            scope = "regular"
        start_time = str(start_sec_int)

    if (start_sec_int !=None or duration != None ) and save_to_disk:
            print "Warning: cannot cache the bar data if start time or duration not set to None!"
            save_to_disk = False

    fbar = None
    if save_to_disk:
        bar_path = settings.DATA_HOME+ '/data/' + date + '/' +symbol+"_second_bar.csv" 
        if os.path.exists(bar_path):
            save_to_disk = False
        else: 
            fbar = open(bar_path, 'w')

    converter = Tick2BarConverter(symbol, date, start_time, scope)

    start_dt = None
    bars = pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume", "average"])
    while True:
        dt, o, h, l, c, v, ave = converter.get_next_bar(interval)
        #print dt, o, h, l, c, v, ave
        if start_dt == None:
            start_dt = dt
        if dt == None:
            if fbar != None:
                fbar.close()
            break
        if duration!= None and (dt-start_dt).seconds > duration:
            #fbar must be None if duration is not None
            break
        bars.append([{"datetime":dt, "open":float(o), "high":float(h), "low":float(l), "close":float(c), "volume":int(v), "average":float(ave)}])
        print bars
        if fbar != None:
            #print "write line"
            #fbar.write(dt.strftime('%Y%m%d%H%M%S') + ", " + o + ", " + h + ", "+ l + ", " + c + ", " + v + ", " + ave + '\n')
            #print type(o), type(ave), type(dt), type(v)
            fbar.write(dt + ", " + str(o) + ", " + str(h) + ", "+ str(l) + ", " + str(c) + ", " + str(v) + ", " + str(ave) + '\n')
            #os.fsync(fbar)

    return bars

def bar2pd(bar_gz_path): 
    dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d%H%M%S')
    bar_pd = pd.read_csv(bar_gz_path, names=["datetime", "open", "high", "low", "close", "volume", "average"], compression="gzip", index_col=[0], parse_dates=[0], date_parser=dateparse)
    return bar_pd


if __name__ == "__main__":
    #ticker = TickDataProcessor()
    #print ticker.get_ticks_by_date("NTRA", "20150702", "20150702")
    #print ticker.get_ticks_by_datetime("NTRA", datetime.strptime("07/02/2015 11:00:00", "%m/%d/%Y %H:%M:%S"), datetime.strptime("07/02/2015 15:00:00", "%m/%d/%Y %H:%M:%S"))
#    print list(tick2bar("NVET", "20150205", save_to_disk=True).iterrows())
    Tick2SecondBarConverter("SPLK", "20120419")
    #print list(tick2bar("BABA", "20140919").iterrows())
