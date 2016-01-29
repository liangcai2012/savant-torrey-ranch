import os, sys
import requests
import socket
import datetime, time
import cjson

from savant.config import settings
from savant.db import session
from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation
from savant.scraper import scrape_ipo, get_company_overview
from savant.scraper.populate_scoop_rate import update_scoop_rate
from savant.ticker.processors import TickDataProcessor
from savant.ticker.analyzers import TickDataAnalyzer
import savant.fetcher.fetch_attick as fetcher
import savant.logger as logger

log = logger.getLogger("db", level="INFO")
tickdata_dir = settings.DOWNLOAD_DIR
data_processor = TickDataProcessor()


def populate_ipo_table():
    ipo_urls = IPOInfoUrl.query.all()
    
    known_unwrs = set()
    
    for url in ipo_urls:
    
        comp = Company.query.filter_by(symbol=url.symbol).first()
        if not comp: 
    #        session.add(comp)
    #        session.commit()
            continue
    
        if HistoricalIPO.query.filter_by(company_id=comp.id).first():
            print "Data exists for:", url.symbol
            continue
    
    #    comp = get_company_overview(url.symbol)
    #    if not comp:
    #        log.warning("Cannot get company info for %s" % url.symbol)
    #        continue
    
    
        ipo_data = scrape_ipo(url.url)
        if ipo_data == {}:
            continue
        log.info("IPO data from NASDAQ.com:\n%s" % cjson.encode(ipo_data))
        underwriters = ipo_data["underwriters"]
        lead_underwriters = ipo_data["lead_underwriters"]
        del ipo_data["underwriters"]
        del ipo_data["lead_underwriters"]
    
        ipo_date = ipo_data["ipo_date"]
        try:
            month, day, year = [int(i) for i in ipo_date.split("/")]
            ipo_date = datetime.date(year, month, day).strftime("%Y%m%d")
            #ipo_data["ipo_date"] = datetime.date(year, month, day).strftime("%Y-%m-%d")
            ipo_data["ipo_date"] = datetime.date(year, month, day)
        except:
            log.error("Error in IPO date:%s" % url.symbol)
            continue
    
        ipo_data_dir = os.path.join(tickdata_dir, ipo_date)
        ipo_data_path = os.path.join(ipo_data_dir, "%s_markethours.csv.gz" % url.symbol)
        exist = False
        if os.path.exists(ipo_data_dir) and os.path.exists(ipo_data_path):
            exist = True
            log.info("IPO data found")
        else:
            request = {"command": "get", "symbol": url.symbol, "date": ipo_date, "gettrade": "true", "getquote": "true"}
            try:
                fetcher_caller = fetcher.FetcherCaller()
                fetcher_caller.set_request(cjson.encode(request))
                response = fetcher_caller.send_request()
                fetcher_caller.close()
            except:
                log.error("Unable to send fetch request")
                continue
    
            count_down = 60
            fetched = False
            while count_down > 0:
                if os.path.exists(ipo_data_path):
                    log.info("IPO data fetched: %s" % url.symbol)
                    fetched = True
                    time.sleep(5)
                    break
                time.sleep(1)
                count_down -= 1
            if not fetched:
                log.error("Unable to download data for %s" % url.symbol)
    
        if exist or fetched:
            itd = process_ipo_tick_data(symbol, ipo_date)
            ipo_data["open_vol"] = itd["open_vol"] 
            ipo_data["first_opening_price"] = itd["first_opening_price"]
            ipo_data["first_closing_price"] = itd["first_closing_price"]
            ipo_data["first_trade_time"] = itd["first_trade_time"]
            ipo_data["first_day_high"] = itd["first_day_high"]
            ipo_data["first_day_low"] = itd["first_day_low"]
            ipo_data["first_day_high_percent_change"] = itd["first_day_high_percent_change"]
            ipo_data["first_day_low_percent_change"] = itd["first_day_low_percent_change"]
            ipo_data["first_day_volume"] = itd["first_day_volume"]
        else:
            ipo_data["open_vol"] = None
            ipo_data["first_opening_price"] = None
            ipo_data["first_closing_price"] = None
            ipo_data["first_trade_time"] = None
            ipo_data["first_day_high"] = None
            ipo_data["first_day_low"] = None
            ipo_data["first_day_high_percent_change"] = None
            ipo_data["first_day_low_percent_change"] = None
            ipo_data["first_day_volume"] = None

        ipo_data["scoop_rating"] = 0 
        ipo_data["company_id"] = comp.id
        log.info("Final IPO data for %s:\n%s" % (url.symbol, ipo_data))
    
        """
        for u in underwriters:
            if u in known_unwrs:
                unwr = Underwriter.query.filter_by(name=u).first()
            else:
                unwr = Underwriter(u)
                known_unwrs.add(u)
            session.add(unwr)
            session.commit()
            a = CompanyUnderwriterAssociation(company_id=comp.id, underwriter_id=unwr.id, lead=False)
            comp.underwriters.append(a)
            session.commit()
    
        for u in lead_underwriters:
            if u in known_unwrs:
                unwr = Underwriter.query.filter_by(name=u).first()
            else:
                unwr = Underwriter(u)
                known_unwrs.add(u)
            session.add(unwr)
            session.commit()
            a = CompanyUnderwriterAssociation(company_id=comp.id, underwriter_id=unwr.id, lead=True)
            comp.underwriters.append(a)
            session.commit()
        """
            
        historical_ipo = HistoricalIPO(**ipo_data)
        session.add(historical_ipo)
        session.commit()

def process_ipo_tick_data(symbol, ipo_date):
    ticks = data_processor.get_ticks_by_date(symbol, ipo_date, ipo_date)
    analyzer = TickDataAnalyzer(ticks)
    return {"open_vol": analyzer.get_open_vol(), 
            "first_opening_price": analyzer.get_opening_price(),
            "first_closing_price": analyzer.get_closing_price(),
            "first_trade_time":  analyzer.get_first_trade_time(),
            "first_day_high":  analyzer.get_high_price(),
            "first_day_low": analyzer.get_low_price(),
            "first_day_high_percent_change": analyzer.get_high_percent_change(),
            "first_day_low_percent_change": analyzer.get_low_percent_change(),
            "first_day_volume": analyzer.get_volume()}

def update_ipo_tick_info():
    ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).filter(HistoricalIPO.open_vol == None).all() 
    for ipo in ipos:
        sym = ipo.Company.symbol
        ipo_date = ipo.HistoricalIPO.ipo_date.strftime('%Y%m%d')
        ipo_data_dir = os.path.join(tickdata_dir, ipo_date)
        ipo_data_path = os.path.join(ipo_data_dir, "%s_markethours.csv.gz" % sym)
        if os.path.exists(ipo_data_dir) and os.path.exists(ipo_data_path):
        #handle exceptions. WLH has trades prior IPO and it does not have market open signal.
#            if sym == 'WLH':
#                open_vol = 1188834
#            elif sym == 'FCAU':
#                open_vol = 242453
#            else:
            print sym 
            ticks = data_processor.get_ticks_by_date(sym, ipo_date, ipo_date)
            analyzer = TickDataAnalyzer(ticks)
            open_vol = analyzer.get_open_vol()
            hi = HistoricalIPO.query.filter(HistoricalIPO.company_id == ipo.Company.id).first()
            if hi == None:
                continue #should not happen
            hi.open_vol= open_vol
            hi.first_opening_price = analyzer.get_opening_price()
            hi.first_closing_price = analyzer.get_closing_price()
            hi.first_trade_time = analyzer.get_first_trade_time()
            hi.first_day_high = analyzer.get_high_price()
            hi.first_day_low = analyzer.get_low_price()
            hi.first_day_high_percent_change = analyzer.get_high_percent_change()
            hi.first_day_low_percent_change = analyzer.get_low_percent_change()
            hi.first_day_volume = analyzer.get_volume()
            #print open_vol
    session.commit()    

def update_ipo_finannce(symbol, ipo_data):
    pass
    


if __name__ == "__main__":
    #populate_ipo_table()
    #make up for missed open_vol
    update_ipo_tick_info()
    #make up for missed financial data
    #update_ipo_finance()

   # update_scoop_rate()
    
