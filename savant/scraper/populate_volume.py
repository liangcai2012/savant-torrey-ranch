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

#create IPOVolume table;
try:
    IOPVolume.__table__.create(bind = savant.db.create_engine())
except:
    savant.db.session.rollback()


#parse tick data and add tick data to row     
    
tickdata_dir = settings.DOWNLOAD_DIR
data_processor = TickDataProcessor()
ipo_urls = IPOInfoUrl.query.all()

known_unwrs = set()

for url in ipo_urls:

    comp = Company.query.filter_by(symbol=url.symbol).first()
    if not comp: 
        continue

    if HistoricalIPO.query.filter_by(company_id=comp.id).first():
        print "Data exists for:", url.symbol
        continue

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
        request = {"command": "get", "symbol": url.symbol, "date": ipo_date}
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
        ticks = data_processor.get_ticks_by_date(url.symbol, ipo_date, ipo_date)
        analyzer = TradeAnalyzer(ticks)
        ipo_data["first_trade_volume"] = analyzer.get_first_trade_volume()
        ipo_data["first_second_volume"] = analyzer.get_first_second_volume()
        ipo_data["first_minute_volume"] = analyzer.get_first_minute_volume()
        ipo_data["first_5m_volume"] = analyzer.get_first_5m_volume()
        ipo_data["first_30m_volume"] = analyzer.get_first_30m_volume()
        ipo_data["first_1h_volume"] = analyzer.get_first_1h_volume()
        ipo_data["first_markethour_volume"] = analyzer.get_first_1d_markethour_vol()
        ipo_data["first_aftermarket_volume"] = analyzer.get_first_1d_aftermarket_vol()
        ipo_data["company_id"] = comp.id
        log.info("Final IPO data for %s:\n%s" % (url.symbol, ipo_data))
    else:
        ipo_data["first_trade_volume"] = 0
        ipo_data["first_second_volume"] = 0
        ipo_data["first_minute_volume"] = 0
        ipo_data["first_5m_volume"] = 0
        ipo_data["first_30m_volume"] = 0
        ipo_data["first_1h_volume"] = 0
        ipo_data["first_markethour_volume"] = 0
        ipo_data["first_aftermarket_volume"]= 0
        ipo_data["company_id"] = comp.id

