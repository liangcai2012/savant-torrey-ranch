import os, requests, sys, datetime
import matplotlib.pyplot as plt
import pandas as pd
import savant.db
from savant.db.models import HistoricalIPO, Company, PostIPOPrice
from savant.config import settings
import numpy as np

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

class ATConnection:
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
        return pd.read_csv(StringIO(connect.content), names=self.bar_names, parse_dates=[0], date_parser=self.bar_parse, index_col=[0])

    def tickData(self, params):
        url = self.root_url + '/tickData'
        return requests.get(url, params=params)
    def optionChain(self, params):
        url = self.root_url + '/optionChain'
        return requests.get(url, params=params)


try:
    PostIPOPrice.__table__.create(bind = savant.db.create_engine())
except:
    savant.db.session.rollback()

def IPO_first_daily_price(symb_list=None):
    at = ATConnection()
    if symb_list is None:
        comps =  Company.query.all()
    else:
        comps =  Company.query.filter(Company.symbol.in_(symb_list)).all()
    for comp in comps:
        ipo =  HistoricalIPO.query.filter_by(company_id=comp.id).first()
        if ipo is None:
            continue
        #print comp.id, ipo
        params = {}
        params['symbol'] = comp.symbol
        params['historyType'] = 1
        params['beginTime'] = ipo.ipo_date.strftime('%Y%m%d%H%M%S')
        params['endTime'] = (ipo.ipo_date + datetime.timedelta(days=10)).strftime('%Y%m%d%H%M%S')
        try:
            prices = at.barData(params=params)
            for ind, price in prices.iterrows():
                post_ipo_price = PostIPOPrice(**price.to_dict())
                #print post_ipo_price
                #post_ipo_price.datetime = price.name
                post_ipo_price.date = price.name.split(' ')[0]
                post_ipo_price.company_id = comp.id
                savant.db.session.add(post_ipo_price)
                savant.db.session.commit()

        except:
            savant.db.session.rollback()
            print "cannot save" + comp.symbol

IPO_first_daily_price()

