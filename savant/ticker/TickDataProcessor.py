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

    def from_file(self, symbol, begin_date, end_date, hours="regular"):
        dates = self.parse_dates(begin_date, end_date)

        if hours == "regular":
            suffix = "_markethours"
        elif hours == "pre":
            suffix = "_premarket"
        elif hours == "after":
            suffix = "_aftermarket"
        else:
            raise ValueError("No such hours: %s" % hours)
        filename = symbol + suffix + ".tsv"

        tick_data = pd.DataFrame(columns=["datetime", "last", "last_size", "last_exch", "cond"])

        for date in dates:
            data_path = os.path.join(self.base_dir, date, filename)
            if not os.path.exists(data_path) and os.path.exists(data_path + ".gz"):
                subprocess.call(["gzip", "-d", os.path.join(data_path + ".gz")])

            cur_ticks = []
            with open(data_path) as f:
                for line in f:
                    if len(cur_ticks) == self.BATCH_SIZE:
                        cur_data = self.from_list(cur_ticks)
                        tick_data = tick_data.append(cur_data)
                    line = line.strip()
                    if line != "":
                        cur_ticks.append(line)
                if len(cur_ticks) > 0:
                    cur_data = self.from_list(cur_ticks)
                    tick_data = tick_data.append(cur_data)

        return tick_data
                        
    def from_list(self, raw_ticks):
        res = defaultdict(list)
        for tick in raw_ticks:
            info = tick.split("\t")
            meta = info[0].strip().split()
            dt = (meta[1] + " " + meta[2]).strip("[]")
            """
            if tick_type = "Quote":
                bid = float(info[1].split(":")[1])
                ask = float(info[2].split(":")[1])
                bid_size = int(info[3].split(":")[1])
                ask_size = int(info[4].split(":")[1])
                bid_exch = int(info[5].split(":")[1])
                ask_exch = int(info[6].split(":")[1])
                cond = int(info[7].split(":")[1])
                t = Quote(dt, bid, ask, bid_size, ask_size, bid_exch, ask_exch, cond)
            """
            if meta[3].upper() == "TRADE":
                last = float(info[1].split(":")[1])
                last_size = int(info[2].split(":")[1])
                last_exch = int(info[3].split(":")[1])
                cond = int(info[4].split(":")[1])
                res["datetime"].append(dt)
                res["last"].append(last)
                res["last_size"].append(last_size)
                res["last_exch"].append(last_exch)
                res["cond"].append(cond)

        df = pd.DataFrame(res)
        columns = ["datetime", "last", "last_size", "last_exch", "cond"]
        return df[columns]

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
    ticker.from_file("CLCD", "20150522", "20150522")
