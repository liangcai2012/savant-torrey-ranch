from bs4 import BeautifulSoup
from savant.db import session, Base
from savant.db.models import Company, IPOInfoUrl, HistoricalIPO
from savant.scraper import get_soup


def scrape_ipo_finance(fin_url):
    fin_data = {}
    
    try:
        soup = get_soup(fin_url)
    except:
        print "Unable to reach or parse url:", fin_url
        return fin_data
    try:
       table = soup.find("div", {"class": "floatL width marginR15px"}).table
       rows = table.find_all("tr")
       for row in rows:
           key = row.td.text.strip()
           if key == "Revenue" or key == "Net Income" or key == "Total Assets":
               key = key.lower().replace(' ', '_')
               value = row.find_all("td")[1].text.replace("$", '').replace(',', '')
               if value.strip(' ') == '--':
                    fin_data[key] = 0
                    continue
               try:
                   fin_data[key] = int(value) 
               except:
                   print 'invalid value', key, value
       table = soup.find("div", {"class": "floatL width"}).table
       rows = table.find_all("tr")
       for row in rows:
           key = row.td.text.strip()
           if key == "Total Liabilities" or key == "Stockholders' Equity":
               key = key.lower().replace(' ', '_').replace("'", '')
               value = row.find_all("td")[1].text.replace("$", '').replace(',', '')
               if value.strip(' ') == '--':
                    fin_data[key] = 0
                    continue
               try:
                   fin_data[key] = int(value) 
               except:
                   print 'invalid value', key, value
    except:
       print "Unable to parse the page: ", fin_url
       return fin_data
    return fin_data

def populate_ipo_finance():
    ipo_urls = IPOInfoUrl.query.all()
    for url in ipo_urls:
        comp = Company.query.filter_by(symbol=url.symbol).first()
        if not comp: 
            continue
        hi = HistoricalIPO.query.filter_by(company_id=comp.id).first()
        if not hi:
            continue
        if hi.revenue != None:
            print "Finance Data existed", url.symbol
            continue
        fin_url = url.url + '?tab=financials'
        fin_data = scrape_ipo_finance(fin_url)
        #print fin_data
        if len(fin_data.keys())< 5:
            print comp.symbol, 'is not updated due to missing financial data', len(fin_data.keys())
            continue
        hi.revenue = fin_data['revenue'] 
        hi.net_income = fin_data['net_income'] 
        hi.total_assets = fin_data['total_assets'] 
        hi.total_liability= fin_data['total_liabilities'] 
        hi.stakeholder_equity = fin_data['stockholders_equity'] 
        session.commit()    


if __name__ == "__main__":
    populate_ipo_finance()
