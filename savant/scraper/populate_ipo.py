import os, sys
import requests
import socket
import datetime, time
import cjson

from savant.config import settings
from savant.db import session
from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation
from savant.scraper import scrape_ipo
from savant.ticker.processors import TickDataProcessor
from savant.ticker.analyzers import TradeAnalyzer
import savant.fetcher.fetch_attick as fetcher
import savant.logger as logger

log = logger.getLogger("db", level="INFO")

tickdata_dir = settings.DOWNLOAD_DIR
data_processor = TickDataProcessor()
ipo_urls = IPOInfoUrl.query.all()

for url in ipo_urls:
    ipo_data = scrape_ipo(url.url)
    log.info("IPO data from NASDAQ.com: %s" % cjson.encode(ipo_data))

    ipo_date = ipo_data["ipo_date"]
    try:
        month, day, year = [int(i) for i in ipo_date.split("/")]
        ipo_date = datetime.date(year, month, day).strftime("%Y%m%d")
        ipo_data["ipo_date"] = datetime.date(year, month, day).strftime("%Y-%m-%d")
    except:
        log.error("Error in IPO date:%s" % url.symbol)
        continue

    ipo_data_dir = os.path.join(tickdata_dir, ipo_date)
    ipo_data_path = os.path.join(ipo_data_dir, "%s_markethours.tsv.gz" % url.symbol)
    if os.path.exists(ipo_data_dir) and os.path.exists(ipo_data_path):
        log.info("IPO data found")
    else:
        request = {"command": "get", "symbol": url.symbol, "date": ipo_date}
        try:
            fetcher_caller = fetcher.FetcherCaller()
            fetcher_caller.set_request(cjson.encode(request))
            response = fetcher_caller.send_request()
        except:
            log.error("Unable to send fetch request")
            break

        count_down = 60
        fetched = False
        while count_down > 0:
            if os.path.exists(ipo_data_path):
                log.info("IPO data fetched: %s" % url.symbol)
                fetched = True
                break
            time.sleep(1)
            count_down -= 1
        if not fetched:
            log.error("Unable to download data for %s" % url.symbol)
            #continue
            break

    ticks = data_processor.from_file(url.symbol, ipo_date, ipo_date)
    analyzer = TradeAnalyzer(ticks)
    ipo_data["first_opening_price"] = analyzer.get_opening_price()
    ipo_data["first_closing_price"] = analyzer.get_closing_price()
    ipo_data["first_trade_time"] = analyzer.get_first_trade_time()
    ipo_data["first_day_high"] = analyzer.get_high_price()
    ipo_data["first_day_low"] = analyzer.get_low_price()
    ipo_data["first_day_high_percent_change"] = analyzer.get_high_percent_change()
    ipo_data["first_day_low_percent_change"] = analyzer.get_low_percent_change()
    ipo_data["first_day_volume"] = analyzer.get_volume()
