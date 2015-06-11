import os, sys
import requests
import socket
import datetime, time
import cjson

from savant.config import settings
from savant.db import session
from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation
from savant.scraper import scrape_ipo
import savant.fetcher.fetch_attick as fetcher
import savant.logger as logger

log = logger.getLogger("db", level="INFO")


# Check if fetcher server is reachable
fetcher_host = settings.FETCHER_HOST
fetcher_port = settings.FETCHER_PORT
try:
    fetcher.check_status("")
except socket.error:
    log.error("Fetcher host unreachable")
    sys.exit(1)

tickdata_dir = os.path.join(settings.OUTPUT_DIR, "data")
fetcher_caller = fetcher.FetcherCaller("")

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
    ipo_data_path = os.path.join(ipo_data_dir, "%s_markethours.tsv.zip" % url.symbol)
    if os.path.exists(ipo_data_dir) and os.path.exists(ipo_data_path):
        log.info("IPO data found")
    else:
        request = {"command": "get", "symbol": url.symbol, "date": ipo_date}
        fetcher_caller.set_request(cjson.encode(request))
        response = fetcher_caller.send_request()

        """
        request = {"command": "check"}
        fetcher_caller.set_request(cjson.encode(request))
        fetcher_state = ""
        while fetcher_state != "Idle":
            response = fetcher_caller.send_request()
            fetcher_state = response["state"]
        """
        count_down = 60
        while count_down > 0:
            if os.path.exists(ipo_data_path):
                log.info("IPO data fetched: %s" % url.symbol)
                break
            time.sleep(1)
            count_down -= 1
        
    raw_input("")
