import matplotlib.pyplot as plt
import pandas as pd
from savant.config import settings
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
#from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc
from matplotlib.finance import * 
import matplotlib.mlab as mlab


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
    #ax.xaxis.set_major_locator(mondays)
    #ax.xaxis.set_minor_locator(alldays)
    #ax.xaxis.set_major_formatter(weekFormatter)
    #ax.xaxis.set_minor_formatter(dayFormatter)
    
    #plot_day_summary_ohlc(ax, quotes, ticksize=3)
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


def singleline(symbol, date, end_min, start_min = 0, pricetype="close"):
    quotes = get_ohlc_from_secondbar(symbol, date, end_min, start_min)
    quotes_df = load_secondbar(symbol, date)
    if quotes_df is None:
        print "data not found"
        return 

    if end_min <= start_min or end_min *60 >= len(quotes_df.index):
        print "Invalid parameters", start_min, end_min
        return 

    quotes = quotes_df[start_min*60: end_min*60]
    # now prepare ax
    fig = plt.figure()
    fig, ax = plt.subplots(figsize=(16, 9))
    #axescolor = '#f6f6f6'  # the axes background colordd

    #ax1 = fig.add_axes(rect1)  # left, bottom, width, height
    axt = ax.twinx()

    quotes.plot(y=pricetype, ax= ax)
    plt.show()
    

singleline("GPRO", "20140626", 30)
#candlestick("GPRO", "20140626", 3)
exit()

