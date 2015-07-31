import os, sys
import httplib
import urllib
import requests
import re
import string
import xlrd
import bs4
from bs4 import BeautifulSoup

from savant.config import settings
from savant.db import session, Base
from savant.db.models import Company, Exchange, Industry, Sector


def get_soup(url, params=None, timeout=5):
    r = requests.get(url, params=params, timeout=timeout)
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    return BeautifulSoup(r.text)

def scrape_yahoo(symbol, full=False):
    """
    Scrape stock data from Yahoo Finance
    
    :param symbol
    :param full
    """

    base_url = "http://finance.yahoo.com/q"
    profile_url = base_url + "/pr"
    key_stat_url = base_url + "/ks"
    params = {"s":symbol}
    data = {"symbol": symbol}

    ## Parsing quote summary page
    try:
        soup = get_soup(base_url, params)
    except:
        print "Could not reach url for", symbol
        return data

    if soup.find("div", {"class": "obsoleteSymbol"}):
        return data

    if full:
        header = soup.find("div", {"class": "yfi_rt_quote_summary"})
        if not header:
            return data
        header = header.find("div", {"class": "title"})
        name = header.h2.text
        data["name"] = name[:name.rindex("(")].strip()
        exch = header.find("span", {"class": "rtq_exch"}).text
        if "Nasdaq" in exch:
            data["exchange"] = "NASDAQ"
        elif "NYSE" in exch:
            data["exchange"] = "NYSE"
        quote_tab = soup.find("div", {"class": "yfi_quote_summary"})
        keys = [k.text.strip(":") for k in quote_tab.find_all("th")]
        values = [v.text for v in quote_tab.find_all("td", {"class": "yfnc_tabledata1"})]
        for key, value in zip(keys, values):
            if key == "Prev Close" and value != "N/A":
                data["prev_close"] = float(value)
            elif key == "Volume" and value != "N/A":
                data["prev_volume"] = int(value.replace(",",""))
            elif key == "Market Cap" and value != "N/A":
                if value.endswith("M"):
                    data["market_cap"] = int(float(value[:-1])*1000000)
                elif value.endswith("B"):
                    data["market_cap"] = int(float(value[:-1])*1000000000)
                elif value.endswith("K"):
                    data["market_cap"] = int(float(value[:-1])*1000)
                else:
                    data["market_cap"] = int(float(value.replace(",","")))
            elif key == "Beta" and value != "N/A":
                data["nasdaq_beta"] = float(value)
            elif "P/E" in key and value != "N/A":
                data["trailing_pe"] = float(value)

    ## Parsing profile page
    try:
        soup = get_soup(profile_url, params)
        profile_tab = soup.find("table", {"class": "yfnc_datamodoutline1"})
        detail_tab_keys = profile_tab.td.find_all("td", {"class": "yfnc_tablehead1"})
        detail_tab_values = profile_tab.td.find_all("td", {"class": "yfnc_tabledata1"})
        for key, value in zip(detail_tab_keys, detail_tab_values):
            if "Sector" in key.text:
                data["sector"] = value.text
            elif "Industry" in key.text:
                data["industry"] = value.text
    except requests.exceptions.HTTPError:
        print "Could not reach profile page for", symbol
    except Exception, e:
        print "Error in parsing profile page for %s: %s" % (symbol, e)
        return data

    try:
        soup = get_soup(key_stat_url, params)
        tab = soup.find("td", {"class": "yfnc_modtitlew2"}).find("table", {"class": "yfnc_datamodoutline1"}).next_sibling
        keys = tab.find_all("td", {"class": "yfnc_tablehead1"})
        values = tab.find_all("td", {"class": "yfnc_tabledata1"})
        for key, value in zip(keys, values):
            if "Float" in key.text:
                fs = value.text
                if fs == "N/A":
                    break
                elif fs.endswith("M"):
                    data["float_shares"] = int(float(fs[:-1])*1000000)
                elif fs.endswith("B"):
                    data["float_shares"] = int(float(fs[:-1])*1000000000)
                elif fs.endswith("K"):
                    data["float_shares"] = int(float(fs[:-1])*1000)
                else:
                    data["float_shares"] = int(fs.replace(",",""))
                break
    except requests.exceptions.HTTPError:
        print "Could not reach key statistics page for", symbol
    except Exception, e:
        print "Error in parsing key statistics page for %s: %s" % (symbol, e)
        return data

    return data

def scrape_nasdaq(symbol):
    base_url = "http://www.nasdaq.com/symbol/" + symbol.lower()
    data = {"symbol": symbol}
    try:
        soup = get_soup(base_url)
    except:
        print "Unable to reach or parse url for", symbol
        return data

    # check if ticker can be found on nasdaq
    if soup.find("div", {"class": "notTradingIPO"}):
        return data
    
    # check if ticker is an ETF
    if soup.find("a", {"id": "etfdetaillink"}):
        return None

    pageheader = soup.find("div", {"id": "qwidget_pageheader"})
    if pageheader==None:
        return data

    header = pageheader.h1.text
    name = header[:header.rindex("Stock")].strip()
    data["name"] = name

    try:
        exch = soup.find("span", {"id": "qbar_exchangeLabel"}).text.split(":")[1].strip()
        data["exchange"] = exch
    except:
        data["exchange"] = "NASDAQ"

    quote_tab = soup.find("table", {"id": "quotes_content_left_InfoQuotesResults"}).div
    trs = quote_tab.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        if tds[0].a:
            key = tds[0].a.strings.next().strip()
        else:
            key = tds[0].text
        if key == "Share Volume":
            data["prev_volume"] = int(tds[1].label.text.replace(",",""))
        elif key == "Previous Close":
            try:
                data["prev_close"] = float(tds[1].text.strip("$ ").replace(",",""))
            except ValueError:
                pass
        elif key == "Market cap":
            try:
                data["market_cap"] = int(tds[1].text.split()[1].replace(",",""))
            except:
                pass
        elif key == "P/E Ratio":
            try:
                data["trailing_pe"] = float(tds[1].text)
            except:
                pass
        elif key == "Beta":
            data["nasdaq_beta"] = float(tds[1].text.replace(",",""))
    return data

def scrape_ipo(url):
    data = {}
    
    try:
        soup = get_soup(url)
    except:
        print "Unable to reach or parse url:", url
        return data
    try:
       table = soup.find("div", {"id": "infoTable"}).table
       rows = table.find_all("tr")
       for row in rows:
           key = row.td.text.strip()
           if key == "Share Price":
               value = row.find_all("td")[1].text.strip("$")
               try:
                   data["price"] = float(value) if "-" not in value else sum([float(i) for i in value.split("-")])/2.0
               except:
                   data["price"] = 0.0
           elif key == "Status":
               data["ipo_date"] = row.find_all("td")[1].text.split("(")[1].strip(")")
           elif key == "Shares Offered":
               value = row.find_all("td")[1].text.replace(",", "")
               data["shares"] = int(value) if value.isdigit() else "N/A"
           elif key == "Shares Outstanding":
               value = row.find_all("td")[1].text.replace("," ,"")
               data["outstanding"] = int(value) if value.isdigit() else "N/A"
   
       exp_table = soup.find("div", {"class": "tab3"}).div.table
       rows = exp_table.find_all("tr")
       data["lead_underwriters"] = []
       data["underwriters"] = []
    except:
       print "Unable to parse the page: ", url
       return data

    for row in rows:
        key = row.td.text.strip()
        if key == "Lead Underwriter":
            data["lead_underwriters"].append(row.find_all("td")[1].text)
        elif key == "Underwriter":
            agent = row.find_all("td")[1].text
            if agent not in data["lead_underwriters"]:
                data["underwriters"].append(row.find_all("td")[1].text)

    return data

def get_company_overview(symbol):
    existing = Company.query.filter_by(symbol=symbol).first()
    if existing:
        return existing

    data = scrape_nasdaq(symbol)
    if not data:
        return None
    elif len(data.keys()) == 1:
        data.update(scrape_yahoo(symbol, full=True))
    else:
        data.update(scrape_yahoo(symbol))

    if len(data) == 1:
        return None

    existing = Company.query.filter_by(name=data["name"]).first()
    if existing:
        return existing

    if "exchange" in data:
        exch = Exchange.query.filter_by(name=data["exchange"]).first()
        if not exch:
            exch = Exchange(name=data["exchange"])
            session.add(exch)
            session.commit()
        del data["exchange"]
        data["exchange_id"] = exch.id

    if "industry" in data:
        indus = Industry.query.filter_by(name=data["industry"]).first()
        if not indus:
            indus = Industry(name=data["industry"])
            session.add(indus)
            session.commit()
        del data["industry"]
        data["industry_id"] = indus.id

    if "sector" in data:
        sect = Sector.query.filter_by(name=data["sector"]).first()
        if not sect:
            sect = Sector(name=data["sector"])
            session.add(sect)
            session.commit()
        del data["sector"]
        data["sector_id"] = sect.id

    comp = Company(**data)
    return comp

def get_symbols(market):
    conn = httplib.HTTPConnection("www.eoddata.com")
    ll = string.uppercase[:26]
    symlist=[]
    for l in ll:
        conn.request("GET", "/stocklist/"+market+"/"+l+".html")
        r = conn.getresponse()
        page = r.read()
        mat = re.findall(r'<tr class=\"r[oe]"[^>]*><td><A.[^>]*>([-A-Z]*)</A>', page, re.M|re.I|re.S)
        symlist += mat
    conn.close()
    return symlist


if __name__ == "__main__":
    symbol = "AAL"
    data = scrape_nasdaq(symbol)
    print data
    if len(data.keys()) == 1:
        data.update(scrape_yahoo(symbol, full=True))
    else:
        data.update(scrape_yahoo(symbol))
    print data
