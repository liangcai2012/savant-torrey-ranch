import sys, datetime
import socket
import requests
import cjson
import pandas as pd
from savant.logger import getLogger
from savant.config import settings

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

log = getLogger("fetcher", level="INFO")
class FetcherCaller:

    def __init__(self, json_request=None):
        if json_request != None:
            self.request = json_request+"\n"
        else:
            self.request = None
        self.connect()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.socket.settimeout(5.0)
        self.socket.connect((settings.FETCHER_HOST, int(settings.FETCHER_PORT)))

    def set_request(self, json_request):
        self.request = json_request+"\n"

    def send_request(self):
        log.info("Request sent: %s" % self.request)
        self.socket.sendall(self.request)
        resp = self.socket.recv(1024)
        log.info("Fetcher response: %s" % resp)
        return resp

#the sync response is used to return data directly rather than write to file. The form : lenth|csv
#len: str of 8 char, eg 00001024
#csv: exactly same as what returned by ATHttpServer
    def send_sync_request(self):
        log.info("Request sent: %s" % self.request)
        self.socket.sendall(self.request)
        resp = self.socket.recv(1024)
        if resp:
            resp_split = resp.split("extra:")
            if len(resp_split) > 1:
                resp_json = cjson.decode(resp_split[0])
            try:
                extra_len = int(resp_json["reslen"])
                extra = resp_split[1]
                remain_len = extra_len + 5 + len(resp_split[0]) - 1024
                while remain_len > 0:
                    resp2 = self.socket.recv(4096)
                    extra += resp2
                    remain_len -= 4096

                log.info("Fetcher returned string of : %d" %extra_len )
                return extra
            except:
                log.error("Invalid response: %s" %resp_split[0])
                return None
            else:
                log.error("No csv data returned: %s" %resp)
                return None
                
        log.error("Receiving nothing")
        return None 

    def close(self):
        self.socket.close()

# type: 0: intraday, 1: daily, 2:weekly
# interval: 1-60, only used when type == 0
def get_bar_data(symbol, type, interval, start, end ):
    json_request = cjson.encode(request)
    caller = FetcherCaller(json_request)    
    caller.send_sync_request()
    caller.close()
    pass


class ATHttpConnection:
    def __init__(self):
        #self.root_url = 'http://127.0.0.1:5000'
        self.bar_names = ['datetime', 'open', 'high', 'low', 'close', 'volume' ]
        self.bar_parse = lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M%S')


    def barData(self, request):
        #url = self.root_url + '/barData'
        #connect = requests.get(url, params=params)
        json_request = cjson.encode(request)
        caller = FetcherCaller(json_request)    
        resp = caller.send_sync_request()
        caller.close()
        if resp is None:
            return None
        try:
            #In case of zero valid record,  ATAPI http server still returns a string of all zero, which would cause date parser error
            return pd.read_csv(StringIO(resp), names=self.bar_names, parse_dates=[0], date_parser=self.bar_parse, index_col=[0])
        except ValueError:
            return None

#sdate/edate must be in the form of 20100101
    def getDailyBar(self, symbol, sdate, edate, weekly):
        if weekly:
            return self.barData({"command":"getbar","symbol":symbol, "historyType": 2, "intradayMinutes": 0,  "beginTime":sdate+"000000", "endTime": edate+"000000"})
        else:
            return self.barData({"command":"getbar","symbol":symbol, "historyType": 1, "intradayMinutes": 0,  "beginTime":sdate+"000000", "endTime": edate+"000000"})

    def getMinuteBar(self, symbol, date, int):
        return self.barData({"command":"getbar","symbol":symbol, "historyType": 0, "intradayMinutes": int,  "beginTime":date+"093000", "endTime": date+"160000"})

    def getHourlyBar(self, symbol, date):
        return self.getMinuteBar(symbol, date, 60)

if __name__ == "__main__":
    ath = ATHttpConnection()
   # print ath.getHourlyBar("DIS", "20160307")
    print ath.getDailyBar("DIS", "20140101", "20151230", False)

"""
class ATHttpConnection:
    def __init__(self):
        self.root_url = 'http://127.0.0.1:5000'
        self.bar_names = ['datetime', 'open', 'high', 'low', 'close', 'volume' ]
        self.bar_parse = lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M%S%f')

    def quoteData(self, params):
        url = self.root_url + '/quoteData'
        return requests.get(url, params=params)

    def quoteStream(self, params):
        url = self.root_url + '/quoteStream'
        return requests.get(url, params=params)

    def barData(self, params):
        url = self.root_url + '/barData'
        connect = requests.get(url, params=params)
        try:
            #In case of zero valid record,  ATAPI http server still returns a string of all zero, which would cause date parser error
            return pd.read_csv(StringIO(connect.content), names=self.bar_names, parse_dates=[0], date_parser=self.bar_parse, index_col=[0])
        except ValueError:
            return None

    def tickData(self, params):
        url = self.root_url + '/tickData'
        return requests.get(url, params=params)

    def optionChain(self, params):
        url = self.root_url + '/optionChain'
        return requests.get(url, params=params)

#sdate/edate must be in the form of 20100101
    def getDailyBar(self, symbol, sdate, edate, weekly):
        params = {}
        params['symbol'] = symbol
        if weekly:
            params['historyType'] = 2 
        else:
            params['historyType'] = 1
        params['beginTime'] = sdate+"000000"
        params['endTime'] = edate+"000000"
        return self.barData(params)

    def getHourlyBar(self, symbol, date):
        params = {}
        params['symbol'] = symbol
        params['intradayMinutes'] = 60 
        params['historyType'] = 0 
        params['beginTime'] = date+"093000"
        params['endTime'] = date+"160000"
        return self.barData(params)

    def getMinuteBar(self, symbol, date, int):
        params = {}
        params['symbol'] = symbol
        params['intradayMinutes'] = int
        params['historyType'] = 0 
        params['beginTime'] = date+"093000"
        params['endTime'] = date+"160000"
        return self.barData(params)

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
