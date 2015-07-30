# coding: utf-8

#get_ipython().magic(u'matplotlib inline')
import socket, os, cjson, requests, sys, datetime
# root_dir = os.path.dirname(__file__)
root_dir = os.getcwd()
import pandas as pd
from sqlalchemy import create_engine # database connection
from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation
from savant.config import settings
from savant.db.models import Exchange, Sector, Industry

#import socket, yaml, os, cjson, requests, sys, datetime

class ATConnection:
    def __init__(self):
        self.root_url = 'http://127.0.0.1:5000'
    def quoteData(self, params):
        url = self.root_url + '/quoteData'
        return requests.get(url, params=params)
    def quoteStream(self, params):
        url = self.root_url + '/quoteStream'
        return requests.get(url, params=params)
    def barData(self, params):
        url = self.root_url + '/barData'
        return requests.get(url, params=params)
    def tickData(self, params):
        url = self.root_url + '/tickData'
        return requests.get(url, params=params)
    def optionChain(self, params):
        url = self.root_url + '/optionChain'
        return requests.get(url, params=params)
at = ATConnection()

ipos = HistoricalIPO.query.all()

prices = {}
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
names = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume' ]
parse = lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M%S%f')

for ipo in ipos:
    comp =  Company.query.filter_by(id=ipo.company_id).first()
    params = {}
    params['symbol'] = comp.symbol
    params['historyType'] = 1
    params['beginTime'] = ipo.ipo_date.strftime('%Y%m%d%H%M%S')
    params['endTime'] = (ipo.ipo_date + datetime.timedelta(days=30)).strftime('%Y%m%d%H%M%S')
    connect = at.barData(params=params)
    try:
        prices[comp.symbol] = pd.read_csv(StringIO(connect.content   ), names=names, parse_dates=[0], date_parser=parse)
    except:
        print comp.symbol


counts = {}
for i in range(6):
    days = {}
    for sym in prices:
        pcd = prices[sym]
        pcd_higher = pcd [pcd["High"] > pcd.iloc[0]["Open"] * ( 1 + i  / 100.0)]
        if pcd_higher.size > 0 and (pcd.index <= pcd_higher.index[0]).sum() < 6:
            days[sym] = (pcd.index <= pcd_higher.index[0]).sum() - 1
        else:
            days[sym] = -1
    result = pd.DataFrame.from_dict (days, orient='index' )
    result.columns = pd.Index(['days'])
    counts[i] = result["days"].value_counts()

len(prices)

for key in counts:
    print 'exceed by ' + str(key) + "%"
    print counts[key]

import matplotlib.pyplot as plt
import math
plt.figure()

for i in range(0, 5):
    y = {}
    for sym in prices:
        try:
            y[sym] = math.floor ((prices[sym].iloc[i]["High"] / prices[sym].iloc[0]["Open"] - 1)* 100 + 0.5)
        except:
            1
    x = pd.DataFrame.from_dict(y, orient='index' )[0].value_counts().sort_index()
    plt.plot(x.index, x.values, '*')
    plt.xlim(0, 20)
    plt.xlabel('excess open price by %')
    plt.ylabel('counts')

plt.savefig('out/price_pk_distri.png')

