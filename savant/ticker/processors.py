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

    def get_ticks(self, symbol, begin_date, end_date, hours="regular"):
        dates = self.parse_dates(begin_date, end_date)

        if hours == "regular":
            suffix = "_markethours"
        elif hours == "pre":
            suffix = "_premarket"
        elif hours == "after":
            suffix = "_aftermarket"
        else:
            raise ValueError("No such hours: %s" % hours)
        filename = symbol + suffix + ".csv.gz"

        tick_data = pd.DataFrame(columns=["date", "time", "type", "price", "size", "exch", "cond"])

        for date in dates:
            data_path = os.path.join(self.base_dir, date, filename)
            cur_ticks = pd.read_csv(data_path, compression="gzip", names=["date", "time", "type", "price", "size", "exch", "cond"])
            tick_data = tick_data.append(cur_ticks)

        return tick_data

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
    print ticker.get_ticks("PGND", "20150521", "20150521")
