import os, sys
import logging
import requests
from savant.db import session
from savant.db.models import IPOInfoUrl
from savant import scraper
from datetime import date

def manual_add_ipo_url():
    ipo_url = IPOInfoUrl('VOXELJET AG', 'VJET', 'http://www.nasdaq.com/markets/ipos/company/voxeljet-ag-915787-73505')
    session.add(ipo_url)
    session.commit()
    
    ipo_url = IPOInfoUrl('AERIE PHARMACEUTICALS INC', 'AERI', 'http://www.nasdaq.com/markets/ipos/company/aerie-pharmaceuticals-inc-684178-73508')
    session.add(ipo_url)
    session.commit()

    ipo_url = IPOInfoUrl('ENDOCHOICE HOLDINGS, INC.', 'GI', 'http://www.nasdaq.com/markets/ipos/company/endochoice-holdings-inc-948923-78332')
    session.add(ipo_url)
    session.commit()

    ipo_url = IPOInfoUrl('STG GROUP, INC.', 'GDEF', 'http://www.nasdaq.com/markets/ipos/company/global-defense-national-security-systems-inc-915709-73501')
    session.add(ipo_url)
    session.commit()

    session.close()
    

def get_ipo_url():
    logging.basicConfig()
    log = logging.getLogger("savant")
    
    base_url = "http://www.nasdaq.com/markets/ipos/activity.aspx?tab=pricings&month="
    
    count = 0
    cur_date = date.today()
    oldest_date = date(2010, 1, 1)
    
    while cur_date >= oldest_date:
        log.info("Getting IPO urls for", cur_date.strftime("%Y-%m"))
        print "Getting IPO urls for", cur_date.strftime("%Y-%m")
        url = base_url + cur_date.strftime("%Y-%m")
        if cur_date.month != 1:
            cur_date = cur_date.replace(month=cur_date.month-1)
        else:
            cur_date = cur_date.replace(year=cur_date.year-1, month=12)
    
        try:
            soup = scraper.get_soup(url)
        except:
            log.info("Could not reach url")
            continue
    
        table = soup.find("div", {"class": "genTable"})
        if "no data" in table.text:
            log.info("No data for %s" % cur_date.strftime("%Y-%m"))
            continue
    
        rows = table.tbody.find_all("tr")
        for row in rows:
            tds = row.find_all("td")
            name = tds[0].text
            url = tds[0].a["href"]
            symbol = tds[1].text
            ipo_url = IPOInfoUrl(name, symbol, url)
            if IPOInfoUrl.query.filter_by(name=name).first() is not None:
                continue
            if IPOInfoUrl.query.filter_by(symbol=symbol).first() is not None:
                continue
            session.add(ipo_url)
    
        session.commit()
    session.close()

manual_add_ipo_url()
