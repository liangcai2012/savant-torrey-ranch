# Import Zipline, the open source backester, and a few other libraries that we will use
import zipline
from zipline import TradingAlgorithm
from zipline.algorithm import LimitOrder
from zipline.api import order, record, symbol, history, add_history

import pytz
from datetime import datetime
import matplotlib.pyplot as pyplot
import numpy as np
import pandas as pd
import savant.models
import datetime

csv_dir = '~/Downloads/1M_SP500_20150211/'
perf_manual = {}
count = 0
for security in savant.models.Company.objects:
    try:
        data = pd.read_csv(csv_dir + security.symbol + '.csv', parse_dates = {"DateTime": [1,2] } , index_col="DateTime")
        data.drop('Symbol', axis=1, inplace=True)
        data.columns = pd.Index([name.lower() for name in data.columns])
        data['price'] = data['close']
        data.index = pd.DatetimeIndex(data.index, tz='UTC')
        data.sort_index(inplace=True)
        data = pd.Panel({security.symbol: data[:data.index[0] + datetime.timedelta(days=10)]} )
        count +=1
        print str(count) + " : " + security.symbol
    except:
        continue

    def initialize(context):
        context.stock = symbol(security.symbol)
        context.traded = False


    def handle_data(context, data):
        if context.traded:
            return
        print data
        order(context.stock, 10000)
        order(context.stock,  - 10000, style=LimitOrder(data[context.stock]['close'] * 1.1))
        context.traded = True

    # NOTE: This cell will take a few minutes to run.

    # Create algorithm object passing in initialize and
    # handle_data functions
    algo_obj = TradingAlgorithm(
        initialize=initialize,
        handle_data=handle_data
    )

    # Run algorithm
    perf_manual[security.symbol] = algo_obj.run(data)
