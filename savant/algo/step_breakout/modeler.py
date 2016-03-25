import warnings
warnings.filterwarnings("ignore", module="matplotlib")
import matplotlib.pyplot as plt
import os, sys, datetime
from sqlalchemy import and_
from savant.db import session
from savant.db.models import Daily, Company, HistoricalIPO
from matplotlib.finance import * 
import matplotlib.dates as mdates
from savant.fetcher import ATHttpConnection
from savant.utils import *
## this is obtain all stocks with a step pattern
#1. abs(close - open) > d% * open
#2. download minute bar for all these 
#3. find out all 


def get_average_vol(symbol, dates):
    ds = Daily.query.filter(Daily.symbol == symbol).filter(and_(Daily.date <= dates[0], Daily.date >= dates[-1])).all()
    len_ds = len(ds)
    if len_ds <1:
        return None
    total_vol = 0
    for d in ds:
       total_vol += d.volume
    return total_vol/len_ds
            
def filter_pattern(change, min_close, min_vol):
    res = []
    ds =  Daily.query.filter(Daily.close- Daily.open>change*Daily.open).filter(and_(Daily.close > min_close, Daily.volume > min_vol)).all()
    for d in ds:
        res.append([d.symbol, d.date, d.open, d.close, d.volume])
    return res

def __get_pages(change, hr_change, min_close, min_vol):
    global _pages, _syms, _dates
    _pages = []
    hr_change_perc = int(100*hr_change)
    
    f1 = filter_pattern(change, min_close, min_vol)
    order = 0
    ath = ATHttpConnection()
    for i in f1:
        his = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).filter(Company.symbol == i[0]).all()
        if len(his)>0 and his[0].HistoricalIPO.ipo_date >= i[1] - datetime.timedelta(25):
            #print "this is in IPO period", i 
            continue
        ave_vol = get_average_vol(i[0], get_previous_dates(i[1], 10))
        if ave_vol is None:
            #print "cannot find average vol", i
            continue
        if i[4] < 3 * ave_vol: 
            #print "vol not exceeding 3 times of everage volume", i
            continue
    
        dates = get_previous_dates(i[1], 15)
        dates.reverse()
        dates += get_following_dates(i[1], 15)
        #print i[0],i[1], len(dates)
        
        ds = Daily.query.filter(Daily.symbol == i[0]).filter(and_(Daily.date >= dates[0], Daily.date <= dates[-1])).all()

        #further filter out high volatile pre-step stocks:
        if False:
            #if (i[2]-ds[0].open) > 0.05 * i[2]:
            #    continue
            qualify = True
            for d in ds:
                if d.date >= i[1]:
                    break
                if abs(d.close-d.open) > 0.03 * d.open:
                    qualify = False
                    break
            if not qualify:
                continue

         #filter by hourly change

        hbar = ath.getHourlyBar(i[0], i[1].strftime("%Y%m%d")) 
        if hbar is None:
            print "no hour bar", i[0], i[1]
        breakout = False
        hr_change_list = []
        for ind, data in hbar.iterrows():
            rate = int(100*(data["close"]-data["open"])/data["open"])
            hr_change_list.append(rate)
            if rate > hr_change_perc:
                breakout = True
        if not breakout:       
            continue
        if hr_change_list[0]>hr_change_perc:
            continue
        print i[0], i[1], hr_change_list

        quotes=[]
        for d in ds:
            quotes.append([date2num(d.date), d.open, d.high, d.low, d.close, d.volume]) 
        _pages.append(quotes)
        _syms.append(i[0])
        _dates.append(i[1])
        order += 1
    return order

def __press(event):
    global _current_page, _fig
    s = _grid[0]*_grid[1]
    if event.key=='n':
        if _current_page+s < len(_pages):
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
    page = _pages[_current_page:]
    
    for i in range(s):
        _axes[(i%s)/c, (i%s)%c].cla()
        _axtes[(i%s)/c][(i%s)%c].cla()
        if i>= len(page):
            continue 
        quotes = page[i] 
        candlestick_ohlc(_axes[(i%s)/c, (i%s)%c], quotes, width=0.3, colorup='g')
        _axes[(i%s)/c, (i%s)%c].set_title(_syms[i+_current_page]+" " +_dates[i+_current_page].strftime("%Y-%m-%d"))

        _axes[(i%s)/c, (i%s)%c].xaxis_date()
        _axes[(i%s)/c, (i%s)%c].xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
        _axes[(i%s)/c, (i%s)%c].autoscale_view()
        plt.setp(_axes[(i%s)/c, (i%s)%c].get_xticklabels(), rotation=45, horizontalalignment='right')

        vmax=0
        for q in quotes:
            vmax=max(vmax, q[5])
        _axtes[(i%s)/c][(i%s)%c].set_ylim(0, 5*vmax)    
        volume_overlay3(_axtes[(i%s)/c][(i%s)%c], quotes, colorup='g')
    plt.suptitle(str(_current_page) + "/"+ str(len(_pages)), verticalalignment="bottom") 


if __name__ == "__main__":
    global _grid, _current_page, _fig, _axes, _axtes
    _pages = []
    _current_page = 0
    _syms = []
    _dates = []
    _grid = [3, 4]
    n = __get_pages(0.1, 0.08, 10, 1000000)
    print "size of results:", n, "size of pages:", len(_pages) 
    exit()

    r = _grid[0]
    c = _grid[1]
    _fig, _axes = plt.subplots(nrows=r, ncols=c, figsize=(16, 9))
    _axtes = [[0 for x in range(c)] for x in range(r)]
    for i in range(r*c):
        _axtes[i/c][i%c]=_axes[i/c, i%c].twinx()
    _current_page = 0
    _fig.canvas.mpl_connect('key_press_event', __press)
    __plot_current_page()
    _fig.tight_layout()
    plt.show()
