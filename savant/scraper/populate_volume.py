import os, requests, sys, datetime
import matplotlib.pyplot as plt
import pandas as pd
import savant.db
from savant.db.models import HistoricalIPO, Company, IPOVolume
from savant.config import settings
import numpy as np

from savant.ticker.analyzers import TickDataAnalyzer
from savant.ticker.processors import TickDataProcessor

HistoricalIPO=HistoricalIPO  #chuan: need instance, unless error
Company =Company     
IPOVolume=IPOVolume   
session=savant.db.session    
TickDataAnalyzer=TickDataAnalyzer

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

#create IPOVolume table;
try:
    IPOVolume.__table__.create(bind = savant.db.create_engine())
except:
    session.rollback()

ticker = TickDataProcessor()


def Populate_IPO_Vol(symb_list=None ,start_date=None, end_date=None):
    if symb_list is None:
        print "sym list is None"
        comps =  Company.query.all()
        return

    for sym,start,end in zip(symb_list,start_date,end_date):
        print 'sym/start/end is: %s ,%s ,%s' %(sym,start,end)
        comps =  Company.query.filter_by(symbol=sym).first()
        print "comp_id is:" ,comps.id
        
        try:
            data = ticker.get_ticks_by_date(sym, start, end, parse_dates=False)
            analyzer = TickDataAnalyzer(data) 
        except:
            print "!!!data file not found for: %s, start:%s,end:%s !!!" %(sym,start,end)
            continue
        
        ipo_data={}
        try:
#         if(1):
            ipo_data["first_trade_vol"] = analyzer.get_first_trade_volume()
            ipo_data["first_second_vol"] = analyzer.get_first_second_vol()
            ipo_data["first_minute_vol"] = analyzer.get_first_minute_vol()
            ipo_data["first_5m_vol"] = analyzer.get_first_5m_vol()
            ipo_data["first_30m_vol"] = analyzer.get_first_30m_vol()
            ipo_data["first_1h_vol"] = analyzer.get_first_1h_vol()
            ipo_data["first_1d_markethour_vol"] = analyzer.get_first_1d_markethour_vol()
            ipo_data["first_1d_aftermarket_vol"] = analyzer.get_first_1d_aftermarket_vol()
            ipo_data["company_id"] = comps.id

            print "ipo_data is: ",ipo_data
            first_trade_volume = IPOVolume(ipo_data)
            session.add(first_trade_volume)
            session.commit()
            print "%s data is committed!" %sym
        except:
#         else:
            session.rollback()
            print "cannot save" + comps.symbol



if __name__ == "__main__":
    print IPOVolume.query
    Populate_IPO_Vol(["FB","EPZM"],["20120518","20130531"],["20120518","20130531"])
    print IPOVolume.query.filter_by(company_id="881").all()
    print IPOVolume.query.all()
#     print IPOVolume.query.delete(synchronize_session='fetch' )


# Jingjing:
# parse tick data and add tick data to row     
     
# tickdata_dir = settings.DOWNLOAD_DIR
# data_processor = TickDataProcessor()
# ipo_urls = IPOInfoUrl.query.all()
# 
# known_unwrs = set()
# 
# for url in ipo_urls:
# 
#     comp = Company.query.filter_by(symbol=url.symbol).first()
#     if not comp: 
#         continue
# 
#     if HistoricalIPO.query.filter_by(company_id=comp.id).first():
#         print "Data exists for:", url.symbol
#         continue
# 
#     ipo_data = scrape_ipo(url.url)
#     if ipo_data == {}:
#         continue
#     log.info("IPO data from NASDAQ.com:\n%s" % cjson.encode(ipo_data))
#     underwriters = ipo_data["underwriters"]
#     lead_underwriters = ipo_data["lead_underwriters"]
#     del ipo_data["underwriters"]
#     del ipo_data["lead_underwriters"]
# 
#     ipo_date = ipo_data["ipo_date"]
#     try:
#         month, day, year = [int(i) for i in ipo_date.split("/")]
#         ipo_date = datetime.date(year, month, day).strftime("%Y%m%d")
#         #ipo_data["ipo_date"] = datetime.date(year, month, day).strftime("%Y-%m-%d")
#         ipo_data["ipo_date"] = datetime.date(year, month, day)
#     except:
#         log.error("Error in IPO date:%s" % url.symbol)
#         continue
# 
#     ipo_data_dir = os.path.join(tickdata_dir, ipo_date)
#     ipo_data_path = os.path.join(ipo_data_dir, "%s_markethours.csv.gz" % url.symbol)
#     exist = False
#     if os.path.exists(ipo_data_dir) and os.path.exists(ipo_data_path):
#         exist = True
#         log.info("IPO data found")
#     else:
#         request = {"command": "get", "symbol": url.symbol, "date": ipo_date}
#         try:
#             fetcher_caller = fetcher.FetcherCaller()
#             fetcher_caller.set_request(cjson.encode(request))
#             response = fetcher_caller.send_request()
#             fetcher_caller.close()
#         except:
#             log.error("Unable to send fetch request")
#             continue
# 
#         count_down = 60
#         fetched = False
#         while count_down > 0:
#             if os.path.exists(ipo_data_path):
#                 log.info("IPO data fetched: %s" % url.symbol)
#                 fetched = True
#                 time.sleep(5)
#                 break
#             time.sleep(1)
#             count_down -= 1
#         if not fetched:
#             log.error("Unable to download data for %s" % url.symbol)
# 
#     if exist or fetched:
#         ticks = data_processor.get_ticks_by_date(url.symbol, ipo_date, ipo_date)
#         analyzer = TradeAnalyzer(ticks)
#         ipo_data["first_trade_volume"] = analyzer.get_first_trade_volume()
#         ipo_data["first_second_volume"] = analyzer.get_first_second_volume()
#         ipo_data["first_minute_volume"] = analyzer.get_first_minute_volume()
#         ipo_data["first_5m_volume"] = analyzer.get_first_5m_volume()
#         ipo_data["first_30m_volume"] = analyzer.get_first_30m_volume()
#         ipo_data["first_1h_volume"] = analyzer.get_first_1h_volume()
#         ipo_data["first_markethour_volume"] = analyzer.get_first_1d_markethour_vol()
#         ipo_data["first_aftermarket_volume"] = analyzer.get_first_1d_aftermarket_vol()
#         ipo_data["company_id"] = comp.id
#         log.info("Final IPO data for %s:\n%s" % (url.symbol, ipo_data))
#     else:
#         ipo_data["first_trade_volume"] = 0
#         ipo_data["first_second_volume"] = 0
#         ipo_data["first_minute_volume"] = 0
#         ipo_data["first_5m_volume"] = 0
#         ipo_data["first_30m_volume"] = 0
#         ipo_data["first_1h_volume"] = 0
#         ipo_data["first_markethour_volume"] = 0
#         ipo_data["first_aftermarket_volume"]= 0
#         ipo_data["company_id"] = comp.id

