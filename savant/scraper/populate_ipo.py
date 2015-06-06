import requests
from savant.config import settings
from savant.db import session
from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation
from savant.scraper import scrape_ipo
import savant.logger as logger

log = logger.getLogger("db")


# Check if fetcher server is reachable
fetcher_host = settings.FETCHER_HOST
fetcher_port = settings.FETCHER_PORT
"""
resp = requests.get("http://%s:%s" % (fetcher_host, fetcher_port))
if resp.status_code != requests.codes.ok:
    log.error("Scraper error: Fetcher host not responding."
    r.raise_for_status()
"""

ipo_urls = IPOInfoUrl.query.all()

for url in ipo_urls:
    ipo_data = scrape_ipo(url.url)
    print ipo_data
