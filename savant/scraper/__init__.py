import os, sys
import requests
import bs4
from bs4 import BeautifulSoup

from savant.config import settings
from savant.db import session, Base
from savant.db.models import Company


def get_soup(url, params, timeout=5):
    r = requests.get(url, params=params, timeout=timeout)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    return BeautifulSoup(r.text)

def scrape_yahoo(symbol):
    base_url = "http://finance.yahoo.com/q"
    profile_url = base_url + "/pr"
    key_stat_url = base_url + "/ks"
    params = {"s":symbol}
    data = {}

    ## Parsing quote summary page
    soup = get_soup(base_url, params)
    quote_tab = soup.find("div", {"class": "yfi_quote_summary"})
    keys = [k.text.strip(":") for k in quote_tab.find_all("th")]
    values = [v.text for v in quote_tab.find_all("td", {"class": "yfnc_tabledata1"})]
    for key, value in zip(keys, values):
        if key == "Prev Close":
            

    ## Parsing profile page
    soup = get_soup(profile_url, params)
    exch = soup.find("span", {"class": "rtq_exch"}).text.strip("- ")
    if "nasdaq" in exch.lower():
        exch = "NASDAQ"
    data["exchange"] = exch

    sum_tab = soup.find("table", {"id": "yfncsumtab"})
    td = sum_tab.find("td", {"class": "yfnc_modtitlew1"})
    data["company"] = td.find("b").text.strip()

    addr_comps = []
    for e in td.find("br").next_elements:
        if not isinstance(e, bs4.element.NavigableString):
            continue
        if "Map" in e:
            break
        elif "\n" in e:
            addr_comps.extend([i.strip(", ") for i in e.split("\n")])
        else:
            addr_comps.append(e.strip("- "))
    data["address"] = ", ".join(addr_comps)

    detail_tab_keys = td.find_all("td", {"class": "yfnc_tablehead1"})
    detail_tab_values = td.find_all("td", {"class": "yfnc_tabledata1"})
    for key, value in zip(detail_tab_keys, detail_tab_values):
        if "Sector" in key.text:
            data["sector"] = value.text
        elif "Industry" in key.text:
            data["industry"] = value.text

    ## Parsing Key Statistics page
    soup = get_soup(key_stat_url, params)
    
