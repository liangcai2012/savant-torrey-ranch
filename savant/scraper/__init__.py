import os, sys
import requests
from bs4 import BeautifulSoup

from savant.config import settings
from savant.db import session, Base
from savant.db.models import Company, Exchange, Industry


def get_soup(url, params, timeout=5):
    r = requests.get(url, params=params, timeout=timeout)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    return BeautifulSoup(r.text)

def scrape_yahoo(symbol):
    base_url = "http://finance.yahoo.com/q"
    profile_url = base_url + "/pr"
    params = {"s":symbol}
    data = {}

    ## Parsing quote summary page
    soup = get_soup(base_url, params)
    quote_tab = soup.find("div", {"class": "yfi_quote_summary"})
    keys = quote_tab.find_all("th")
    values = quote_tab.find_all("td", {"class": "yfnc_tabledata1"})
    for key, value in zip(keys, values):
        print key.text + ": " + value.text

    ## Parsing profile page
    soup = get_soup(profile_url, params)
    sum_tab = soup.find("table", {"id": "yfncsumtab"})
    td = sum_tab.find("td", {"class": "yfnc_modtitlew1"})
    data["company"] = td.find("b").text.strip()
    detail_tab_keys = td.find_all("td", {"class": "yfnc_tablehead1"})
    detail_tab_values = td.find_all("td", {"class": "yfnc_tabledata1"})
    for key, value in zip(detail_tab_keys, detail_tab_values):
        if "Sector" in key.text:
            data["sector"] = value.text
        elif "Industry" in key.text:
            data["industry"] = value.text
    print data

def collect_company_info():
    data = {"symbol": "BABA", "name": "Alibaba Group Holding Limited", "exchange": "NYSE", "headquarter": "Hangzhou, China", "yahoo_sector": "Services", "yahoo_industry": "Specialty Retail, Other", "google_sector": "N/A", "google_industry": "N/A", "outstanding_shares": 2500000000, "floating_shares": 1040000000, "prev_close": 88.40, "prev_volume": 11017929, "trailing_pe": 56.63}
    res = Exchange.query.filter_by(name=data["exchange"]).first()
    if res is None:
        session.add(Exchange(name=data["exchange"], origin="us"))
    print Exchange.query.filter_by(name=data["exchange"]).first()
    #comp = Company(**data)


if __name__ == "__main__":
    collect_company_info()
