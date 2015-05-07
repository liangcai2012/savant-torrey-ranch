import os, sys
import requests
from bs4 import BeautifulSoup

from savant.config import settings
from savant.db import session, Base
from savant.db.models import Companies


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
    
