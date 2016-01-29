import datetime
import savant.db
from savant.db import session
from savant.config import settings
from savant.db.models import MarketIndex, Daily 
import yahoo_finance as yahoo

def create_daily_table():
    try:
        Daily.__table__.create(bind = savant.db.create_engine())
    except:
        savant.db.session.rollback()
 
def insert_daily_bar(symbol, date, open, high, low, close, volume):
    rec = {"symbol": symbol, "date": date, "open": open, "high": high, "low": low, "close": close, "volume": volume, "tick_downloaded": False, "minbar_downloaded": False} 
    d= Daily(**rec)
    savant.db.session.add(d)
   # savant.db.session.commit()
   # return True
    try:
        savant.db.session.commit()
        #print symbol, "daily info added for ", date
        return True
    except:
        savant.db.session.rollback()
        #print symbol, "daily info cannot be added for ", date 
        return False


#AT does not provide data for market index, so this uses yahoo API
#sdate and edate must be of format "2000-01-05"
def scrap_daily_bar(symbol, sdate, edate):
    stock = yahoo.Share(symbol)
    results = stock.get_historical(sdate, edate)
    #the result contains: adj_close and close. THe adj_close should have considered divident or split. we use close here. 
    print len(results)
    if len(results) == 0:
        print "cannot download historical data from Yahoo Finance for", symbol
    nInserted = 0
    for res in results:
        if insert_daily_bar(symbol, datetime.datetime.strptime(res["Date"], '%Y-%m-%d'), res["Open"], res["High"], res["Low"], res["Close"], res["Volume"]):
            nInserted += 1
    print nInserted, "records were added"


#first set all tick_downloaded and minbar_downlaoded to False
#then scan the file system and update the two flags accordingly 
def scan_update_daily():
    pass

if __name__ == "__main__":
    create_daily_table()
    #scrap_daily_bar("^DJI", "2010-01-01", "2016-01-01")
    scrap_daily_bar("^GSPC", "2010-01-01", "2016-01-01")
    scrap_daily_bar("^NDX", "2010-01-01", "2016-01-01")
