import urllib
import datetime
import httplib
import re
import string

def getMarketMovers(time_period,num_symbols):
    # Rank NASDAQ and NYSE stocks based on average trading volume of the given time period
    # and return the top num_symbols stocks
    stock_data = {}

    symlist = getListFromEoddata("NASDAQ")
    symlist += getListFromEoddata("NYSE")
    
    from_date,to_date = getDates(time_period)
    print "Here's what your urls look like:\n",buildURL("",from_date,to_date)
    for symbol in symlist:
	url = buildURL(symbol,from_date,to_date)
	for i in range(3):
	    try:
 		f = urllib.urlopen(url)
		content = f.read()
		if content.find("404 Not Found") != -1:
		    break
	    	    continue
		quotes = content.strip().split('\n')
    		stock_data[symbol] = calcAvgVolume(quotes)
	    except:
		print "Error retrieving data for %s, trying again..." % symbol
    if num_symbols != "all":
    	return sorted(stock_data.keys(),key=lambda symbol:stock_data[symbol],reverse=True)[:num_symbols]
    else:
	return sorted(stock_data.keys(),key=lambda symbol:stock_data[symbol],reverse=True)

def buildURL(symbol,from_date,to_date):
    # Build query string for historcal quotes from Yahoo Finance
    url = "http://ichart.yahoo.com/table.csv?s=" + symbol
    for i,j in zip(["a","b","c","d","e","f"],[from_date.month-1,from_date.day,from_date.year,to_date.month-1,to_date.day,to_date.year]):
	url += "&"+i+"="+str(j)
    url += "&g=d&ignore=.csv"
    return url

def getDates(period):
    # Get the begin and end dates for the query; end date is always yesterday
    today = datetime.date.today()
    d = datetime.timedelta(days=1)
    to_date = today - d
    d = datetime.timedelta(days=period)
    from_date = to_date - d
    return from_date,to_date

def calcAvgVolume(quotes):
    # Calculate average trading volume for the given daily quotes
    days = len(quotes) - 1
    total_volume = 0
    for quote in quotes[1:]:
	total_volume += int(quote.split(',')[-2])	
    return total_volume/float(days)

def getListFromEoddata(market):
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
    market_movers = getMarketMovers(30,"all")
    print ",".join(market_movers)
