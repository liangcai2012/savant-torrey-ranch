#! /usr/local/bin/python

import warnings
warnings.filterwarnings("ignore", module="matplotlib")
import argparse as ap
import sys
import matplotlib.pyplot as plt
import pandas as pd
from savant.config import settings
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
#from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
from matplotlib.finance import * 
import matplotlib.mlab as mlab
from savant.scraper import ATHttpConnection


#this is just to test how numpy recarray is used 
def csvtest():
    startdate = datetime.date(2016, 1, 1)
    today = enddate = datetime.date.today()
    ticker = 'SPY'
    fh = fetch_historical_yahoo(ticker, startdate, enddate)
    r = mlab.csv2rec(fh)
    fh.close()
    r.sort()
    prices = r.adj_close
    print prices
    deltas = np.zeros_like(prices)
    deltas[1:] = np.diff(prices)
    print deltas
    up = deltas > 0
    print up
    print r.date[up]
    print r.date[~up]


def plot_candlestick(quote):
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(bottom=0.2)

    candlestick_ohlc(ax, quote, width=0.000004, colorup='g')

    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

    axt = ax.twinx()
    quote[0][5]/=1000
    vmax=0
    for q in quote:
        vmax=max(vmax, q[5])
    axt.set_ylim(0, 5*vmax)    
    volume_overlay3(axt, quote, colorup='g')
    
    fig.tight_layout()
    plt.show()

def plot_line(quote_df, pricetype, volsuppress):
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(bottom=0.2)
    axt = ax.twinx()
    quote_df.plot(y=pricetype, ax= ax)
    if volsuppress != 0:
        quote_df.iloc[0, 4]/=volsuppress
    vmax=0
    for ind, q in quote_df.iterrows():
        vmax=max(vmax, q["volume"])
    axt.set_ylim(0, 5*vmax)
    quote_df.plot(y="volume", ax=axt, kind="area", color='#008000')
    #quotes.plot(y=pricetype, ax= ax, kind="area", color='g')

    fig.tight_layout()
    plt.show()


def load_secondbar(symbol, date):
    bar_gz_path = settings.DATA_HOME+ '/data/' +  date + '/' +symbol+"_second_bar.csv.gz" 
    if not os.path.exists(bar_gz_path):
        return None
    col = ["time", "open", "high", "low", "close", "volume", "average"]
    dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d%H%M%S')
    quotes_df  = pd.read_csv(bar_gz_path, names=col, index_col=[0], parse_dates=[0], date_parser=dateparse)
    return quotes_df

# return [seconds, price, volume]
def get_ohlc_from_secondbar(symbol, date,  end_min, start_min = 0):
    quotes_df = load_secondbar(symbol, date)
    if quotes_df is None:
        return None

    if end_min <= start_min or end_min *60 >= len(quotes_df.index):
        return None

    quotes_slice = quotes_df[start_min*60: end_min*60]

    quotes=[]
    quotes_iter = quotes_slice.iterrows()
    for i, row in quotes_iter:
        quotes.append([date2num(i), row["open"], row["high"], row["low"], row["close"], row["volume"]]) 
    return quotes


def candlestick(symbol, date, end_min, start_min = 0):
    quotes = get_ohlc_from_secondbar(symbol, date, end_min, start_min)
    if quotes: 
        plot_candlestick(quotes)
    else: 
        print "data not found"
    return


def sencond_bar_line(symbol, date, end_min, start_min = 0, pricetype="close"):
    quotes = get_ohlc_from_secondbar(symbol, date, end_min, start_min)
    quotes_df = load_secondbar(symbol, date)
    if quotes_df is None:
        print "data not found"
        return 

    if end_min <= start_min or end_min *60 >= len(quotes_df.index):
        print "Invalid parameters", start_min, end_min
        return 

    quotes = quotes_df[start_min*60: end_min*60]
    plot_line(quotes, "open")
    return


def minute_bar_line(symbol, date, interval=1, pricetype="close", volsuppress=0):
    ath = ATHttpConnection()
    quotes_df = ath.getMinuteBar(symbol, date, interval) 
    if quotes_df is None:
        print "data not found"
        return 

    plot_line(quotes_df, pricetype, volsuppress)
    return

def test():    
    minute_bar_line("ADMS", "20151223")
    #sencond_bar_line("LOCO", "20140725", 120)
    #candlestick("LOCO", "20140725", start_min=0, end_min=120)
    #sencond_bar_line("GPRO", "20140626", 30)
    #candlestick("GPRO", "20140626", 3)

def view_dayline(args):
    pass

def view_minline(args):
    interval = args.interval 
    pricetype = args.price_type
    volsuppress = args.vol_suppress
    symdate = args.symdate
    if len(symdate) > 1:
        print "multiple plot not supported yet..."
    symdate_split = symdate[0].split(":")
    if len(symdate_split) != 2:
        print "invalid symdate format. it should be SYM:yyyymmdd"
    minute_bar_line(symdate_split[0], symdate_split[1], interval, pricetype, volsuppress)

def view_secline(args):
    pass

def view_daycan():
    pass
 

def view_mincan(args):
    pass

def view_seccan(args):
    pass

if __name__ == "__main__":
    parser = ap.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands")

    subparsers = parser.add_subparsers(help="subcommands")
    psr_secline = subparsers.add_parser("dayline",help="view daily bar with single line." )
    psr_secline.add_argument("sym_dayrange",nargs="+",help="symbol and date range to be displayed. eg.: MSFT:20140212:20150101. In case when a -s option exists, the daterange only need one date.")
    psr_secline.add_argument("-t","--price_type",type=str,default="open", help="type of price to be displayed, could be open/high/low/close, default is open")
    psr_minline.add_argument("-9","--grid",type=str,default=33, help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_minline.add_argument("-s","--span",type=int,default=30, help="show number of days following the single date specified in sym_dayrange. It can be negative, which means show date proceeding"))
    psr_minline.add_argument("-i","--interval",type=int,default=1, help="value can be either 1(daily bar) or 7(weekly bar)"))
    psr_secline.set_defaults(func=view_dayline)    


    psr_minline = subparsers.add_parser("minline",help="view minutes bar.")
    psr_minline.add_argument("symdate",nargs="+",help="symbol and date to be displayed. symbol and data seperated with :")
    psr_minline.add_argument("-i","--interval",type=int,default=1, help="min bar interval, could be 1-60, default is 1")
    psr_minline.add_argument("-t","--price_type",type=str,default="open", help="type of price to be displayed, could be open/high/low/close, default is open")
    psr_minline.add_argument("-s","--vol_suppress",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_minline.add_argument("-9","--grid",type=str,default=33, help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_minline.set_defaults(func=view_minline)    


    psr_secline = subparsers.add_parser("secline",help="view second bar. Data from local storage. Make sure data is ready")
    psr_secline.add_argument("symdate_minrange",nargs="+",help="symbol, date and minute range to be displayed. eg.: MSFT:20140212:0:3. Showing too much second data can make the plot very slow.")
    psr_secline.add_argument("-t","--price_type",type=str,default="open", help="type of price to be displayed, could be open/high/low/close, default is open")
    psr_secline.add_argument("-s","--first_vol_suppressed",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_minline.add_argument("-9","--grid",type=str,default=33, help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_secline.set_defaults(func=view_secline)    


    psr_mincan = subparsers.add_parser("daycan",help="view daily bar candlestick.")
    psr_secline.add_argument("sym_dayrange",nargs="+",help="symbol and date range to be displayed. eg.: MSFT:20140212:20150101. In case when a -s option exists, the daterange only need one date.")
    psr_secline.add_argument("-t","--price_type",type=str,default="open", help="type of price to be displayed, could be open/high/low/close, default is open")
    psr_minline.add_argument("-9","--grid",type=str,default=33, help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_minline.add_argument("-s","--span",type=int,default=30, help="show number of days following the single date specified in sym_dayrange. It can be negative, which means show date proceeding"))
    psr_minline.add_argument("-i","--interval",type=int,default=1, help="value can be either 1(daily bar) or 7(weekly bar)"))
    psr_mincan.set_defaults(func=view_daycan)    


    psr_mincan = subparsers.add_parser("mincan",help="view minutes candlestick.")
    psr_mincan.add_argument("symdate",nargs="+",help="symbol and date to be displayed. symbol and data seperated with :")
    psr_mincan.add_argument("-i","--interval",type=int,default=1, help="min bar interval, could be 1-60, default is 1")
    psr_mincan.add_argument("-s","--first_vol_suppressed",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_minline.add_argument("-9","--grid",type=str,default=33, help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_mincan.set_defaults(func=view_mincan)    


    psr_mincan = subparsers.add_parser("mincan",help="view minutes candlestick.")
    psr_mincan.add_argument("symdate",nargs="+",help="symbol and date to be displayed. symbol and data seperated with :")
    psr_mincan.add_argument("-i","--interval",type=int,default=1, help="min bar interval, could be 1-60, default is 1")
    psr_mincan.add_argument("-s","--first_vol_suppressed",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_minline.add_argument("-9","--grid",type=str,default=33, help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_mincan.set_defaults(func=view_mincan)    


    psr_seccan = subparsers.add_parser("seccan",help="view second candlestick. Data from local storage. Make sure data is ready")
    psr_seccan.add_argument("symdate_minrange",nargs="+",help="symbol, date and minute range to be displayed. eg.: MSFT:20140212:0:3. Showing too much second data can make the plot very slow.")
    psr_seccan.add_argument("-s","--first_vol_suppressed",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_minline.add_argument("-9","--grid",type=str,default=33, help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_seccan.set_defaults(func=view_seccan)    


    args = parser.parse_args()
    args.func(args)

