#! /usr/local/bin/python

import warnings
warnings.filterwarnings("ignore", module="matplotlib")
import argparse as ap
import sys, datetime
import matplotlib.pyplot as plt
import pandas as pd
from savant.config import settings
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
#from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
from matplotlib.finance import * 
import matplotlib.mlab as mlab
import matplotlib.dates as mdates
from savant.scraper import ATHttpConnection
from savant.utils import *

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

def get_date_span(date, before, after):
    format_str = '%Y%m%d'
    the_date = datetime.datetime.strptime(date, format_str)
    start = (the_date-datetime.timedelta(days = before)).strftime(format_str)
    end = (the_date+datetime.timedelta(days = after)).strftime(format_str)
    return start, end


#----------plot on given fig/ax/axt, used by both single plot or grid plot ---------------------
# plot candlestick with volume overlay
def plot_candlestick(fig, ax, axt, quote_df, volsuppress, title, barwidth):
    quote_list=[]
    quotes_iter = quote_df.iterrows()
    for i, row in quotes_iter:
        quote_list.append([date2num(i), row["open"], row["high"], row["low"], row["close"], row["volume"]]) 

    candlestick_ohlc(ax, quote_list, width=barwidth, colorup='g')

    ax.xaxis_date()
    ax.autoscale_view()
    ax.set_title(title)
    plt.setp(ax.get_xticklabels(which='both'), rotation=45, horizontalalignment='right')

    if volsuppress != 0:
        quote_list[0][5]/=1000
    vmax=0
    for q in quote_list:
        vmax=max(vmax, q[5])
    axt.set_ylim(0, 5*vmax)    
    volume_overlay3(axt, quote_list, colorup='g')
    

# plot line with volume overlay, quote in dataframe format
def plot_line(fig, ax, axt, quote_df, pricetype, volsuppress, title):
    quote_df.plot(y=pricetype, ax= ax, legend=None)

   # ax.xaxis_date()
   # ax.autoscale_view()
    ax.set_title(title)
    plt.setp(ax.get_xticklabels(which='both'), rotation=45, horizontalalignment='right')
    
    if volsuppress != 0:
        quote_df.iloc[0, 4]/=volsuppress
    vmax=0
    for ind, q in quote_df.iterrows():
        vmax=max(vmax, q["volume"])
    axt.set_ylim(0, 5*vmax)
    quote_df.plot(y="volume", ax=axt, kind="area", color='#008000', legend=None)

#---------------load data ------------------------
# we will use load_dailybar_atserver for now
def load_dailybar_localdb(symbol, start_date, end_date):
    pass

# first we need to use at service more to detect potential out-of-service, secondly this one support weekly quotes 
def load_dailybar_atserver(symbol, start_date, end_date, weekly):
    ath = ATHttpConnection()
    quote_df = ath.getDailyBar(symbol, start_date, end_date, weekly) 
    return quote_df

def load_minutebar_atserver(symbol, date, interval):
    ath = ATHttpConnection()
    quote_df = ath.getMinuteBar(symbol, date, interval) 
    return quote_df

def load_secondbar_localfs(symbol, date, start_min, end_min):
    bar_gz_path = settings.DATA_HOME+ '/data/' +  date + '/' +symbol+"_second_bar.csv.gz" 
    if not os.path.exists(bar_gz_path):
        return None
    col = ["time", "open", "high", "low", "close", "volume", "average"]
    dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d%H%M%S')
    quote_df  = pd.read_csv(bar_gz_path, names=col, index_col=[0], parse_dates=[0], date_parser=dateparse)
    if quote_df is None:
        return None

    if end_min <= start_min or end_min *60 >= len(quote_df.index):
        return None

    quote_slice = quote_df[start_min*60: end_min*60]
    return quote_slice


# return [seconds, price, volume]

#args: sym_dayrange(s), grid, span, internval, price_type(only for line figure)
def view_day(args, fig_type):
    pricetype=None
    if fig_type == "line":
        pricetype = args.price_type
    interval = args.interval 
    if interval != 1 and interval != 7:
        print "invalid interval, only 1 or 7 is supported"
        return
    weekly = False
    if interval == 7:
        weekly = True
    span = args.span
    sdr = args.sym_dayrange
    if len (sdr) > 1:
        grid_split = args.grid.split(":")
        if len(grid_split)!=2:
            print "invalid grid dimention", grid_split
            return
        #prepare _dflist and _title
        dflist = []
        title = []
        for s in sdr:
            s_split = s.split(":")
            if len(s_split) !=3  and (len(s_split) != 2 or span == ""):
                print "invalid sym_dayrange format. It should be SYM:yyyymmdd or SYM:yyyymmdd:yyyymmdd", s
                return
            symbol = s_split[0]
            if len(s_split) == 2:
                span_split = span.split(":")
                start, end = get_date_span(s_split[1], int(span_split[0]), int(span_split[1]))
            else:
                start = s_split[1]
                end = s_split[2]
            quote_df = load_dailybar_atserver(symbol, start, end, weekly)
            if quote_df is None:
                continue
            dflist.append(quote_df)
            title.append(s+" "+span)
            
        #kick start the plot
        __plot_multi(int(grid_split[0]), int(grid_split[1]), dflist, title, fig_type, pricetype, 0, 0.1)
        return
    sdr_split = sdr[0].split(":")
    if len(sdr_split) !=3  and (len(sdr_split) != 2 or span == ""):
        print "invalid sym_dayrange format. It should be SYM:yyyymmdd or SYM:yyyymmdd:yyyymmdd", sdr[0]
        return
    symbol = sdr_split[0]
    if len(sdr_split) == 2:
        span_split = span.split(":")
        start, end = get_date_span(sdr_split[1], int(span_split[0]), int(span_split[1]))
    else:
        start = sdr_split[1]
        end = sdr_split[2]
        
    quote_df = load_dailybar_atserver(symbol, start, end, weekly)
    if quote_df is None:
        print "data not found"
        return 

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(bottom=0.2)
    axt = ax.twinx()

    if fig_type == "line":
        plot_line(fig, ax, axt, quote_df, pricetype, 0, sdr[0]+' '+span)
    else:
        plot_candlestick(fig, ax, axt, quote_df, 0, sdr[0]+' '+span, 0.1)

    fig.tight_layout()
    plt.show()
    return

#args: symdate(s), interval, volsuppress, grid, pricetype(line only)
def view_min(args, fig_type):
    interval = args.interval 
    pricetype=None
    if fig_type == "line":
        pricetype = args.price_type
    volsuppress = args.vol_suppress
    symdate = args.symdate
    if len(symdate) > 1:
        grid_split = args.grid.split(":")
        if len(grid_split)!=2:
            print "invalid grid dimention", grid_split
            return
        #prepare _dflist and _title
        dflist = []
        title = []
        for sd in symdate:
            sd_split = sd.split(":")
            if len(sd_split) != 2:
                print "invalid symdate format. it should be SYM:yyyymmdd", sd
                return
            quote_df = load_minutebar_atserver(sd_split[0], sd_split[1], interval)
            if quote_df is None:
                continue
            dflist.append(quote_df)
            title.append(sd)

        #kick start the plot
        __plot_multi(int(grid_split[0]), int(grid_split[1]), dflist, title, fig_type, pricetype, volsuppress, 0.0004)
        return
    symdate_split = symdate[0].split(":")
    if len(symdate_split) != 2:
        print "invalid symdate format. it should be SYM:yyyymmdd", symdate[0]
        return

    quote_df = load_minutebar_atserver(symdate_split[0], symdate_split[1], interval)
    if quote_df is None:
        print "data not found"
        return 

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(bottom=0.2)
    axt = ax.twinx()

    if fig_type == "line":
        plot_line(fig, ax, axt, quote_df, pricetype, volsuppress, symdate[0])
    else:
        plot_candlestick(fig, ax, axt, quote_df, volsuppress, symdate[0], 0.0004)
        
    fig.tight_layout()
    plt.show()
    return

#args: symdate_minrange(s), volsuppress, grid, pricetype(line only)
def view_sec(args, fig_type):
    volsuppress = args.vol_suppress
    pricetype = None 
    if fig_type == "line":
        pricetype = args.price_type
    symdate_minrange = args.symdate_minrange
    if len(symdate_minrange) > 1:
        grid_split = args.grid.split(":")
        if len(grid_split)!=2:
            print "invalid grid dimention", grid_split
            return
        #prepare _dflist and _title
        dflist = []
        title = []
        for sdmr in symdate_minrange:
            sdmr_split = sdmr.split(":")
            if len(sdmr_split) != 4:
                print "invalid symdate format. it should be SYM:yyyymmdd:start_min:end_min", sdmr
                return

            quote_df = load_secondbar_localfs(sdmr_split[0], sdmr_split[1], int(sdmr_split[2]), int(sdmr_split[3]))
            if quote_df is None:
                continue
            dflist.append(quote_df)
            title.append(sdmr)

        #kick start the plot
        __plot_multi(int(grid_split[0]), int(grid_split[1]), dflist, title, fig_type, pricetype, volsuppress, 0.000005)

        return
    sdmr_split = symdate_minrange[0].split(":")
    if len(sdmr_split) != 4:
        print "invalid symdate format. it should be SYM:yyyymmdd:start_min:end_min", symdate_minrange[0]
        return

    quote_df = load_secondbar_localfs(sdmr_split[0], sdmr_split[1], int(sdmr_split[2]), int(sdmr_split[3]))
    if quote_df is None:
        print "data not found"
        return 

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.subplots_adjust(bottom=0.2)
    axt = ax.twinx()

    if fig_type == "line":
        plot_line(fig, ax, axt, quote_df, pricetype, volsuppress, symdate_minrange[0])
    else:
        plot_candlestick(fig, ax, axt, quote_df, volsuppress, symdate_minrange[0], symdate_minrange[0], 0.000005)

    fig.tight_layout()
    plt.show()
    return


# ----------functions for plotting in grid ----------------
def __press(event):
    global _current_page, _fig
    s = _grid[0]*_grid[1]
    if event.key=='n':
        if _current_page+s < len(_dflist):
            _current_page += s 
            __plot_current_page()
            plt.draw()
            print("redrawed next")
            sys.stdout.flush()
    elif event.key=='p':
        if _current_page >= s: 
            _current_page -= s 
            __plot_current_page()
            plt.draw()
            print("redrawed prev")
            sys.stdout.flush()
    else:
        print('press either n or p to display next or previous grid')
        sys.stdout.flush()

def __plot_current_page():
    global _axes, _axtes
    s = _grid[0]*_grid[1]
    r = _grid[0]
    c = _grid[1]
    page = _dflist[_current_page:]
    page_title = _title[_current_page:]
    

    for i in range(s):
        ax = _axes[i/c, i%c]
        axt = _axtes[i/c][i%c]
        ax.cla()
        axt.cla()

        if i>= len(page):
            continue 

        quote_df = page[i] 
        title = page_title[i]
        if _fig_type == "line":
            plot_line(_fig, ax, axt, quote_df, _price_type, _vol_suppress, title)

        else:
            plot_candlestick(_fig, ax, axt, quote_df, _vol_suppress, title, _bar_width)

    plt.suptitle(str(_current_page) + "/"+ str(len(_dflist)), verticalalignment="bottom") 

def __plot_multi(row, col, dflist, title, figtype, pricetype, volsuppress, barwidth):
    global _current_page, _grid, _fig, _axes, _axtes, _dflist, _title, _fig_type,  _price_type, _vol_suppress, _bar_width 
    _current_page = 0
    _grid = [row, col]
    _dflist = dflist
    _title = title
    _fig_type = figtype
    _price_type = pricetype 
    _vol_suppress = volsuppress
    _bar_width = barwidth

    _fig, _axes = plt.subplots(nrows=row, ncols=col, figsize=(16,9))
    _axtes = [[0 for x in range(col)] for x in range(row)]
    for i in range(row*col):
        _axtes[i/col][i%col]=_axes[i/col, i%col].twinx()
    _fig.canvas.mpl_connect('key_press_event', __press)
    __plot_current_page()
    _fig.tight_layout()
    plt.show()



#--------cmd handlers ----------
def view_dayline(args):
    view_day(args,"line")

def view_daycan(args):
    view_day(args, "can")

def view_minline(args):
    view_min(args, "line")

def view_mincan(args):
    view_min(args, "can")

def view_secline(args):
    view_sec(args, "line")

def view_seccan(args):
    view_sec(args, "can")

if __name__ == "__main__":
    parser = ap.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands")

    psr_dayline = subparsers.add_parser("dayline",help="view daily bar with single line." )
    psr_dayline.add_argument("sym_dayrange",nargs="+",help="symbol and date range to be displayed. eg.: MSFT:20140212:20150101. In case when a -s option exists, the daterange only need one date.")
    psr_dayline.add_argument("-t","--price_type",type=str,default="open", help="type of price to be displayed, could be open/high/low/close, default is open")
    psr_dayline.add_argument("-s","--span",type=str, default="", help="show number of days procceding and following the single date specified in sym_dayrange. eg: 3:3 means show date from date-3 to date+3")
    psr_dayline.add_argument("-i","--interval",type=int,default=1, help="value can be either 1(daily bar) or 7(weekly bar)")
    psr_dayline.add_argument("-g","--grid",type=str,default="3:3", help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_dayline.set_defaults(func=view_dayline)


    psr_minline = subparsers.add_parser("minline",help="view minutes bar.")
    psr_minline.add_argument("symdate",nargs="+",help="symbol and date to be displayed. symbol and data seperated with :")
    psr_minline.add_argument("-i","--interval",type=int,default=1, help="min bar interval, could be 1-60, default is 1")
    psr_minline.add_argument("-t","--price_type",type=str,default="open", help="type of price to be displayed, could be open/high/low/close, default is open")
    psr_minline.add_argument("-v","--vol_suppress",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_minline.add_argument("-g","--grid",type=str,default="3:3", help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_minline.set_defaults(func=view_minline)    


    psr_secline = subparsers.add_parser("secline",help="view second bar. Data from local storage. Make sure data is ready")
    psr_secline.add_argument("symdate_minrange",nargs="+",help="symbol, date and minute range to be displayed. eg.: MSFT:20140212:0:3. Showing too much second data can make the plot very slow.")
    psr_secline.add_argument("-t","--price_type",type=str,default="open", help="type of price to be displayed, could be open/high/low/close, default is open")
    psr_secline.add_argument("-v","--vol_suppress",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_secline.add_argument("-g","--grid",type=str,default="3:3", help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_secline.set_defaults(func=view_secline)    


    psr_daycan = subparsers.add_parser("daycan",help="view daily bar candlestick.")
    psr_daycan.add_argument("sym_dayrange",nargs="+",help="symbol and date range to be displayed. eg.: MSFT:20140212:20150101. In case when a -s option exists, the daterange only need one date.")
    psr_daycan.add_argument("-s","--span",type=str, default="", help="show number of days procceding and following the single date specified in sym_dayrange. eg: 3:3 means show date from date-3 to date+3")
    psr_daycan.add_argument("-i","--interval",type=int,default=1, help="value can be either 1(daily bar) or 7(weekly bar)")
    psr_daycan.add_argument("-g","--grid",type=str,default="3:3", help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_daycan.set_defaults(func=view_daycan)    


    psr_mincan = subparsers.add_parser("mincan",help="view minutes candlestick.")
    psr_mincan.add_argument("symdate",nargs="+",help="symbol and date to be displayed. symbol and data seperated with :")
    psr_mincan.add_argument("-i","--interval",type=int,default=1, help="min bar interval, could be 1-60, default is 1")
    psr_mincan.add_argument("-v","--vol_suppress",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_mincan.add_argument("-g","--grid",type=str,default="3:3", help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_mincan.set_defaults(func=view_mincan)    


    psr_seccan = subparsers.add_parser("seccan",help="view second candlestick. Data from local storage. Make sure data is ready")
    psr_seccan.add_argument("symdate_minrange",nargs="+",help="symbol, date and minute range to be displayed. eg.: MSFT:20140212:0:3. Showing too much second data can make the plot very slow.")
    psr_seccan.add_argument("-v","--vol_suppress",type=int,default=0, help="how volume in first record to be suppressed, default is 0 means no suppression, in displaying IPC data its typical value is 1000")
    psr_seccan.add_argument("-g","--grid",type=str,default="3:3", help="grid of subplots when displaying multiple symbol. eg. 3x4, only needed when sydate has more than 1 argement")
    psr_seccan.set_defaults(func=view_seccan)    


    args = parser.parse_args()
    args.func(args)

