#! /usr/bin/python

import re
import httplib
import string

from StaticInfo import * 

MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def getListFromEoddata(conn, market):
    ll = string.uppercase[:26]
    symlist=[]
    cnamelist = []
    for l in ll:
        conn.request("GET", "/stocklist/"+market+"/"+l+".html")
        r = conn.getresponse()
        page = r.read()
        mat = re.findall(r'<tr class=\"r[oe]"[^>]*><td><A[^>]*>([-A-Z]*)</A></td><td>([^<]*)</td>', page, re.M|re.I|re.S)
	
    	#print mat 
	#exit(0)
	#stocklist is a list of tuple (sym, cname)
        stocklist += mat

    return symlist, cnamelist 

def getIPOFromYahoo():
    conn = httplib.HTTPConnection("biz.yahoo.com")
    ll = string.lowercase[:26]
    symlist=[]
    sharelist=[]
    pricelist=[]
    datelist=[]
    for l in ll:
        conn.request("GET", "/ipo/comp_"+l+".html")
        r = conn.getresponse()
        page = r.read()
        mat = re.findall(r'<TR><TD>[^<]*</TD><TD><a\shref[^>]*>([-A-Z]*)</a></TD><TD>([^<]*)<small>M</small></TD><TD[^>]*>([^<]*)</TD><TD[^>]*>[^<]*</TD><TD[^>]*>([^<]*)</TD><TD>Priced</td>', page, re.M|re.I|re.S)
        for mi in mat:
            symlist.append(mi[0])
            sharelist.append(mi[1])
            pricelist.append(mi[2])
            datelist.append(mi[3])
    return symlist, sharelist, pricelist, datelist 

    
def getGoogleSector(conn, sym):
    conn.request("GET", "/finance?q="+sym)
    r = conn.getresponse()
    page = r.read()
    mat = re.findall(r'Sector:\s<a[^>]*>([^<]*?)</a>', page, re.M|re.I|re.S)
    if len(mat) > 1:
        print "abnorbal sector info for ", sym
        sector = ''
    elif len(mat) == 0:
        sector = ''
    else:
        sector = mat[0].replace("&amp;", "&")
    mat = re.findall(r'Industry:\s<a[^>]*>([^<]*?)</a>', page, re.M|re.I|re.S)
    if len(mat) > 1:
        print "abnorbal industry info for ", sym
        industry = ""
    elif len(mat) == 0:
        industry = ""
    else:
        industry = mat[0].replace("&amp;", "&")
    return sector, industry

def getYahooSector(conn, sym):
    conn.request("GET", "/q/pr?s="+sym+"+Profile")
    r = conn.getresponse()
    page = r.read()
    mat = re.findall(r'<td[^>]*>Sector:</td><td[^>]*><a[^>]*>([^<]*?)</a>', page, re.M|re.I|re.S)
    if len(mat) > 1:
        print "abnorbal sector info for ", sym
        sector = ''
    elif len(mat) == 0:
        sector = ''
    else:
        sector = mat[0]
    mat = re.findall(r'<td[^>]*>Industry:</td><td[^>]*><a[^>]*>([^<]*?)</a>', page, re.M|re.I|re.S)
    if len(mat) > 1:
        print "abnorbal industry info for ", sym
        industry = '' 
    elif len(mat) == 0:
        industry = ''
    else:
        industry = mat[0]
    return sector, industry



def getfromFile():
    path = '../../data/meta/stocklist.csv'
    try:
        fs = open(path, 'r')
    except IOError:
        return []
    fs.readline()   #skip the first line
    symlist = []
    for line in fs:
        sym = line.split(',')[0]
        if len(sym) != 0:
            symlist.append(sym)
    return symlist


def main():

# pull list from eoddata
    print 'Getting complete stock list from eoddata.com...'
    conn_eoddata = httplib.HTTPConnection("www.eoddata.com")

    nasdaqlist= getListFromEoddata(conn_eoddata, "NASDAQ")
    nyselist= getListFromEoddata(conn_eoddata, "NYSE")
    
    conn_eoddata.close()

# get list from database
    si = StaticInfo()
    si.open()

    existing_nasdaq_symlist = si.getstocklist("NASDAQ")
    existing_nyse_symlist = si.getstocklist("NYSE")

    #existinglist = getfromFile()
    missing_nasdaqlist=[]
    for sym in nasdaqlist:
        if sym[0] not in existing_nasdaqi_symlist:
            missing_nasdaqlist.append(sym)
    
    missing_nyselist=[]
    for sym in nyselist:
        if sym[0] not in existing_nyse_symlist:
            missing_nyselist.append(sym)
    

    if len(missing_nasdaqlist) != 0 or len(missing_nyselist) != 0:
    	conn_google = httplib.HTTPConnection("www.google.com")
    	conn_yahoo = httplib.HTTPConnection("finance.yahoo.com")

        for sym in missing_nasdaqlist:
            gsec, gind = getGoogleSector(conn_google, market+'%3A'+sym[0])
            ysec, yind = getYahooSector(conn_yahoo, sym[0])
            si.update(sym[0], 'NASDAQ', None, sym[1], gsec, gind, ysec, yind)
        for sym in missing_nyselist:
            gsec, gind = getGoogleSector(conn_google, market+'%3A'+sym[0])
            ysec, yind = getYahooSector(conn_yahoo, sym[0])
            si.update(sym[0], 'NYSE', None, sym[1], gsec, gind, ysec, yind)  

      	conn_google.close()
       	conn_yahoo.close()

    si.close()
    print 'Number of new stocks is', len(missing_nyselist) + len(missing_nasdaqlist)
	
    
    #print 'Getting IPO data from Yahoo...'
    #iposym, iposhare, ipoprice, ipodate= getIPOFromYahoo()
    
    #    if sym in iposym:
    #        index = iposym.index(sym)
    #        ishare = iposhare[index] 
    #        iprice = ipoprice[index] 
    #        idate= ipodate[index] 
    #        idatesplit = idate.split('-')
    #        try:
    #            idatenorm = str(int(idatesplit[2])*10000 + (MONTH.index(idatesplit[1]) +1)*100 + int(idatesplit[0]))
    #        except ValueError:
    #            print "invalid month", sym, idate
    #
    #
    #    print sym, ',', market, ',', gsec, ',', gind, ',', ysec, ',', yind, ',', idatenorm,',', iprice, ',', ishare 
   #     count += 1


if __name__ == "__main__":
	main()

