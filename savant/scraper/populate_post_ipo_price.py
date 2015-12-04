import time, datetime
import yahoo_finance as yahoo

import savant.db
from savant.db.models import * 
from savant.db import session
from savant.config import settings
from savant.ticker.processors import *
from savant.db.models import HistoricalIPO, Company, PostIPOPriceYahoo, PostIPOPriceAT
from savant.scraper.download_after_ipo_prices import IPO_first_daily_price



#shows only 2 out of 900 do not have post ipo bar data from AT or Yahoo
def check_missing_post_ipo():
    ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
    for ipo in ipos:
        symbol = ipo.Company.symbol
        date = str(ipo.HistoricalIPO.ipo_date).replace('-', '')
        tick_gz_path = settings.DATA_HOME + '/data/' + date + '/' + symbol + '_markethours.csv.gz'
        if os.path.exists(tick_gz_path):
            #pips  = PostIPOPriceAT.query.filter(PostIPOPriceAT.company_id ==ipo.HistoricalIPO.company_id).filter(PostIPOPriceAT.date == ipo.HistoricalIPO.ipo_date).all()
            pips  = PostIPOPriceYahoo.query.filter(PostIPOPriceYahoo.company_id ==ipo.HistoricalIPO.company_id).filter(PostIPOPriceYahoo.date == ipo.HistoricalIPO.ipo_date).all()
            if len(pips) < 1:
            #    print 'no bar from yahoo', ipo.Company.symbol
                pip_at = PostIPOPriceYahoo.query.filter(PostIPOPriceAT.company_id ==ipo.HistoricalIPO.company_id).filter(PostIPOPriceAT.date == ipo.HistoricalIPO.ipo_date).all()
                if len(pip_at) < 1:
                    print 'no bar data', symbol
  
def find_split_stocks():
    ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
    for ipo in ipos:
        symbol = ipo.Company.symbol
        date = str(ipo.HistoricalIPO.ipo_date).replace('-', '')
        tick_gz_path = settings.DATA_HOME + '/data/' + date + '/' + symbol + '_markethours.csv.gz'
        if os.path.exists(tick_gz_path):
            pips_at  = PostIPOPriceAT.query.filter(PostIPOPriceAT.company_id ==ipo.HistoricalIPO.company_id).filter(PostIPOPriceAT.date == ipo.HistoricalIPO.ipo_date).all()
            pips_yh  = PostIPOPriceYahoo.query.filter(PostIPOPriceYahoo.company_id ==ipo.HistoricalIPO.company_id).filter(PostIPOPriceYahoo.date == ipo.HistoricalIPO.ipo_date).all()
            if len(pips_at) < 1 or len(pips_yh) < 1:
                continue
            o_at = pips_at[0].open
            o_yh = pips_yh[0].open
            ratio = (2.0*max(o_at, o_yh))/min(o_at, o_yh)
            #after split the price might be x or x.5 times of the other
            if abs(o_at - o_yh) > 1 and ratio%1 < 0.01 and ratio < 500:
                print symbol, o_at, o_yh


##
#validity = 0: Good
#validity = 1: no tick data
#validity = 2: incomplete tick (usually smaller open day volume)
#validity = 3: suspicious vol (small open vol and smaller day volume than yahoo)
#validity = 4: mismatch open (small open vol and mismatch open price 

def check_ipo_data_validity():
    ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
    for ipo in ipos:
        symbol = ipo.Company.symbol
        date = str(ipo.HistoricalIPO.ipo_date).replace('-', '')
        tick_gz_path = settings.DATA_HOME + '/data/' + date + '/' + symbol + '_markethours.csv.gz'
        if not os.path.exists(tick_gz_path):
            hi = HistoricalIPO.query.filter(HistoricalIPO.company_id == ipo.Company.id).first()
            if hi is not None:
                hi.validity= 1 
                session.commit()    
        else:
            o_at = o_yh = v_at = v_yh = 0 
            pips_at  = PostIPOPriceAT.query.filter(PostIPOPriceAT.company_id ==ipo.HistoricalIPO.company_id).filter(PostIPOPriceAT.date == ipo.HistoricalIPO.ipo_date).all()
            pips_yh  = PostIPOPriceYahoo.query.filter(PostIPOPriceYahoo.company_id ==ipo.HistoricalIPO.company_id).filter(PostIPOPriceYahoo.date == ipo.HistoricalIPO.ipo_date).all()
            if len(pips_at) > 0:
                o_at = pips_at[0].open
                v_at = pips_at[0].volume
            if len(pips_yh) > 0:
                o_yh = pips_yh[0].open
                v_yh = pips_yh[0].volume
            open_vol = ipo.HistoricalIPO.open_vol
            if v_at <  v_yh/1.2:
                print 'incomplete tick--', symbol, 'at:', o_at, v_at, 'yh:', o_yh, v_yh, 'open_vol:', open_vol 
                hi = HistoricalIPO.query.filter(HistoricalIPO.company_id == ipo.Company.id).first()
                if hi is not None:
                    hi.validity= 2
                    session.commit()    
                continue
            if ipo.HistoricalIPO.open_vol < 5000:
                #only if one of at or yh data is not present
                if min(v_at, v_yh) == 0 or float(max(v_at, v_yh)/min(v_at, v_yh)) > 1.2 or abs(o_at - o_yh) < 0.02:
                    print 'suspicious volume--', symbol, 'at:', o_at, v_at, 'yh:', o_yh, v_yh, 'open_vol:', open_vol 
                    hi = HistoricalIPO.query.filter(HistoricalIPO.company_id == ipo.Company.id).first()
                    if hi is not None:
                        hi.validity= 3
                    session.commit()    
                    continue
            #if float(max(v_at, v_yh))/min(v_at, v_yh) > 1.5 and float(max(v_at, v_yh)/min(v_at, v_yh))< 2.0:
            #if float(max(v_at, v_yh))/min(v_at, v_yh) < 1.2 :   #vol match, does not matter
                if abs(o_at - o_yh) > 0.02:
                    hi = HistoricalIPO.query.filter(HistoricalIPO.company_id == ipo.Company.id).first()
                    if hi is not None:
                        hi.validity= 4 
                    session.commit()    
                    print 'mismatch open--', symbol, 'at:', o_at, v_at, 'yh:', o_yh, v_yh, 'open_vol:', open_vol 
                    continue   # open price match 



def populate_post_ipo_at(days=30):
    IPO_first_daily_price(days)


def populate_post_ipo_yahoo(days=30):
    try:
        PostIPOPriceYahoo.__table__.create(bind = savant.db.create_engine())
    except:
        savant.db.session.rollback()
    
    #ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).filter(HistoricalIPO.first_day_volume != None).filter(Company.symbol == 'TRTLU').all() 
    ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).filter(HistoricalIPO.first_day_volume != None).all() 
    for ipo in ipos:
        sym = ipo.Company.symbol
        print sym
        stock = yahoo.Share(sym)
        ipo_date = ipo.HistoricalIPO.ipo_date
        sdate = ipo_date.strftime('%Y-%m-%d')
        edate = (ipo_date+ datetime.timedelta(days)).strftime('%Y-%m-%d')
        result = stock.get_historical(sdate, edate)
        #the result contains: adj_close and close. THe adj_close should have considered divident or split. we use close here. 
        if len(result) == 0:
            print "cannot download historical data from Yahoo Finance for", sym
            continue
        try:
            if sdate != result[-1]["Date"]:
                print "historical data on ipo date for", sym, "is not found"
                continue
        except:
            print "result for ", sym, 'does not contain Date:', result[-1] 
            continue
        if len(result) < 12: 
            print sym, 'contains only', len(result), 'daily bar!'
            continue
        for res in result:
            try:
                rec = {"open": float(res["Open"]), "close": float(res["Close"]), "high": float(res["High"]), "low": float(res["Low"]), "volume": int(res["Volume"]), "date": datetime.datetime.strptime(res["Date"], '%Y-%m-%d')}
            except:
                print "invalide result for", sym, res
                break
    
            post_ipo_price = PostIPOPriceYahoo(**rec)
            #print post_ipo_price
            #post_ipo_price.datetime = price.name
    #        post_ipo_price.date = price.name.split(' ')[0]
            #post_ipo_price.date = res["Date"]
            post_ipo_price.company_id = ipo.Company.id
            savant.db.session.add(post_ipo_price)
            try:
                savant.db.session.commit()
            except:
                savant.db.session.rollback()
                print "cannot save ", sym
    
        #vol = result[0]["Volume"]
        #rate = int(vol)*1.0/ipo.HistoricalIPO.first_day_volume
        #if rate > 1.1:
        #print sym, ipo.HistoricalIPO.first_day_volume, vol



if __name__ == "__main__":
    #find_split_stocks()
    #populate_post_ipo_at()
    #check_missing_post_ipo()
    check_ipo_data_validity()

