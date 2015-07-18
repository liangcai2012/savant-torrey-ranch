"""
import os, sys
import requests

from savant.config import settings
from savant.logger import getLogger

log = getLogger("fetcher", level="INFO")

class HTTPAPICaller:
    DEFAULT_BEGIN_TIME = "060000"
    DEFAULT_END_TIME = "200000"
    DEFAULT_TIME_WINDOW = 3600
    MIN_INTERVAL = 60

    def __init__(self):
        self.config()

    def config(self):
        self.host = "http://127.0.0.1" if settings.FETCHER_HOST == "localhost" else settings.FETCHER_HOST
        self.port = settings.FETCHER_PORT
        self.base_url = self.host + ":" + self.port + "/"
        resp = requests.get(self.base_url)
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

        self.download_dir = settings.DOWNLOAD_DIR

    def fetch_daily_tick_data(self, symbol, date, get_trades=True, get_quotes=True):
        params = {"symbol": symbol, "beginTime": begin_time, "endTime": end_time}
        if get_trades:
            params["trades"] = 1
        else:
            params["trades"] = 0
        if get_quotes:
            params["quotes"] = 1
        else:
            params["quotes"] = 0
        data = self.make_call("tickData", params)
        # save data to disk
        
        self.save_to_disk(data)

    def make_call(self, command, params):
        resp = requests.get(self.base_url + command + "?", params=params)
        if resp.status_code == requests.codes.ok:
            return resp.text
        else:
            log.error("No response from server")
            return False

    def save_to_disk(self, data, filepath):
        with open(filepath, "w") as o:
            o.write(data)

if __name__ == "__main__":
    caller = HTTPAPICaller()
    caller.set_request({"command": "tickData", "symbol": "MSFT", "trades": 1, "quotes": 0, "beginTime": "20101103153000", "endTime": "20101103160000"})
    resp = caller.make_call()
"""
