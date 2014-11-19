import re
import httplib
import string

MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

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
    return symlist 

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



print 'Getting complete stock list from eoddata.com...'
nasdaqlist = getListFromEoddata("NASDAQ")
print "Number of stocks on NASDAQ is", len(nasdaqlist)
nyselist = getListFromEoddata("NYSE")
print "Number of stocks on NYSE is", len(nyselist)
symlist = nasdaqlist + nyselist
existinglist = getfromFile()
missedlist=[]
for sym in nasdaqlist:
    if sym not in existinglist:
        missedlist.append(sym)

for sym in nyselist:
    if sym not in existinglist:
        missedlist.append(sym)

print 'Number of new stocks is', len(missedlist)

print 'Getting IPO data from Yahoo...'
iposym, iposhare, ipoprice, ipodate= getIPOFromYahoo()

conn_google = httplib.HTTPConnection("www.google.com")
conn_yahoo = httplib.HTTPConnection("finance.yahoo.com")

count = 0
for sym in missedlist:
    if count < len(nasdaqlist):
        market = 'NASDAQ'
    else:
        market = 'NYSE'
    gsec, gind = getGoogleSector(conn_google, market+'%3A'+sym)
    ysec, yind = getYahooSector(conn_yahoo, sym)
    ishare =''
    iprice = ''
    idate = ''
    idatenorm = ''

    if sym in iposym:
        index = iposym.index(sym)
        ishare = iposhare[index] 
        iprice = ipoprice[index] 
        idate= ipodate[index] 
        idatesplit = idate.split('-')
        try:
            idatenorm = str(int(idatesplit[2])*10000 + (MONTH.index(idatesplit[1]) +1)*100 + int(idatesplit[0]))
        except ValueError:
            print "invalid month", sym, idate


    print sym, ',', market, ',', gsec, ',', gind, ',', ysec, ',', yind, ',', idatenorm,',', iprice, ',', ishare 
    count += 1
conn_google.close()
conn_yahoo.close()
