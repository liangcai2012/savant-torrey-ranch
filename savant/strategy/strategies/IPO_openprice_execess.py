import os, requests, sys, datetime
import matplotlib.pyplot as plt
import math
import pandas as pd
from sqlalchemy import create_engine # database connection
from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation
from savant.config import settings
from savant.db.models import Exchange, Sector, Industry
import sqlite3
import numpy as np

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

class ATConnection:
    def __init__(self):
        self.root_url = 'http://127.0.0.1:5000'
        self.bar_names = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume' ]
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
        return pd.read_csv(StringIO(connect.content), names=self.bar_names, parse_dates=[0], date_parser=self.bar_parse, index_col=[0])

    def tickData(self, params):
        url = self.root_url + '/tickData'
        return requests.get(url, params=params)
    def optionChain(self, params):
        url = self.root_url + '/optionChain'
        return requests.get(url, params=params)


def IPO_first_daily_price(symb_list):
    at = ATConnection()
    comps =  Company.query.filter(Company.symbol.in_(symb_list)).all()
    prices = {}

    for comp in comps:
        ipo =  HistoricalIPO.query.filter_by(company_id=comp.id).first()
        params = {}
        params['symbol'] = comp.symbol
        params['historyType'] = 1
        params['beginTime'] = ipo.ipo_date.strftime('%Y%m%d%H%M%S')
        params['endTime'] = (ipo.ipo_date + datetime.timedelta(days=30)).strftime('%Y%m%d%H%M%S')
        try:
            prices[comp.symbol] = at.barData(params=params)
        except:
            print comp.symbol
    return prices

def plot_IPO_excess_dist(symb_list, save_fig_path=False):
    prices = IPO_first_daily_price(symb_list)
    plt.figure()

    for i in range(0, 5):
        y = {}
        for sym in prices:
            try:
                y[sym] = (prices[sym].iloc[i]["High"] / prices[sym].iloc[0]["Open"] - 1)* 100
            except:
                1
        x = pd.DataFrame.from_dict(y, orient='index' )[0].value_counts().sort_index()
        x_cum = pd.Series.copy( x)
        for ind in x.index:
            if ind < 0:
                x_cum[ind] = x[x.index <= ind].sum()
            else:
                x_cum[ind] = x[x.index >= ind].sum()

        plt.plot(x.index, x_cum.values *1.0 / x.values.sum(), '-*')
        plt.xlim(-1, 20)
        plt.xlabel('excess open price by %')
        plt.ylabel('% percent')
    if save_fig_path:
        plt.savefig(str(save_fig_path))
    plt.show()

def prices_count(prices):
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

    for key in counts:
        print 'exceed by ' + str(key) + "%"
        print counts[key]

if __name__ == "__main__":
    plot_IPO_excess_dist( [u'AAVL', u'ABY', u'AKBA', u'BLCM', u'CLDN'])
