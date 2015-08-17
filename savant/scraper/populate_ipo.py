import os, sys
import requests
import socket
import datetime, time
import cjson

from savant.config import settings
from savant.db import session
from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation
from savant.scraper import scrape_ipo, get_company_overview
from savant.ticker.processors import TickDataProcessor
from savant.ticker.analyzers import TradeAnalyzer
import savant.fetcher.fetch_attick as fetcher
import savant.logger as logger

log = logger.getLogger("db", level="INFO")

tickdata_dir = settings.DOWNLOAD_DIR
data_processor = TickDataProcessor()
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
        ipo_data["first_opening_price"] = analyzer.get_opening_price()
        ipo_data["first_closing_price"] = analyzer.get_closing_price()
        ipo_data["first_trade_time"] = analyzer.get_first_trade_time()
        ipo_data["first_day_high"] = analyzer.get_high_price()
        ipo_data["first_day_low"] = analyzer.get_low_price()
        ipo_data["first_day_high_percent_change"] = analyzer.get_high_percent_change()
        ipo_data["first_day_low_percent_change"] = analyzer.get_low_percent_change()
        ipo_data["first_day_volume"] = analyzer.get_volume()
        ipo_data["scoop_rating"] = "N/A"
        ipo_data["company_id"] = comp.id
        log.info("Final IPO data for %s:\n%s" % (url.symbol, ipo_data))
    else:
        ipo_data["first_opening_price"] = 0.0
        ipo_data["first_closing_price"] = 0.0
        ipo_data["first_trade_time"] = "N/A"
        ipo_data["first_day_high"] = 0.0
        ipo_data["first_day_low"] = 0.0
        ipo_data["first_day_high_percent_change"] = 0.0
        ipo_data["first_day_low_percent_change"] = 0.0
        ipo_data["first_day_volume"] = 0.0
        ipo_data["scoop_rating"] = "N/A"
        ipo_data["company_id"] = comp.id

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
    
