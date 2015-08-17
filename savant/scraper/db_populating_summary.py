from savant.db.models import * 
from savant.db import session
from savant.config import settings
from datetime import date
import time
from savant.ticker.processors import *


def listExpiredIPOSym():
   symbols = []
   comps =  Company.query.all()
   for comp in comps:
      symbols.append(comp.symbol)
   urls = IPOInfoUrl.query.filter(~IPOInfoUrl.symbol.in_(symbols)).all()
   syms = []
   for url in urls:
      syms.append(url.symbol)
   return syms

def listReplicatedIPOSym():
   ipo_symbols = [] 
   repl_symbols = []
   iius = IPOInfoUrl.query.all()
   for iiu in iius:
      if iiu.symbol in ipo_symbols:
         repl_symbols.append(iiu.symbol)
      else:
         ipo_symbols.append(iiu.symbol)
   return repl_symbols
 
def getHistorySym():
   symbols = []
   his = HistoricalIPO.query.all()
   for hi in his:
      comp = Company.query.filter(Company.id==hi.company_id).all()
      if len(comp) >1:
         print comp
      if comp[0].symbol in symbols:
         print 'replicated', comp[0].symbol
      symbols.append(comp[0].symbol)
   return symbols


def listDuplicatedSym():
   ipo_symbols = [] 
   iius = IPOInfoUrl.query.all()
   for iiu in iius:
         ipo_symbols.append(iiu.symbol)
   symbols = getHistorySym()
   #print len(symbols)
   urls = IPOInfoUrl.query.filter(~IPOInfoUrl.symbol.in_(symbols)).all()
   syms = []
   for url in urls:
      syms.append(url.symbol)
   return syms

def diffTickDB():
   try:
      with open('./list', 'r+') as f:
         symfilelist=f.read().split('\n')[:-1]
      print len(symfilelist), 'ipo symbols were feteched'
   except:
      print "list file not found, please run find ../../out/  -name '*markethour*' >list  and then edit the file to keep just symbol"
      return

   symlist = getHistorySym()
   clist = []
   cs = Company.query.filter(Company.symbol.in_(symlist)).all()
   for c in cs:
      clist.append({"id":c.id, "symbol":c.symbol})

   s=[]
   for sf in symfilelist:
      if sf not in symlist:
         s.append(sf)
   s1=[]
   s2=[]
   for c in clist:
      if c["symbol"] not in symfilelist:
         hi = HistoricalIPO.query.filter(HistoricalIPO.company_id==c["id"]).first()
         if hi.ipo_date <= date(2010, 7, 1):
            s1.append(c["symbol"])
         else:
            s2.append(c["symbol"])
   return s, s1, s2


def diffIPOBar():

   ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 

   bar = session.query(PostIPOPrice.company_id).distinct()
   bsym =[b[0] for b in bar]
   miss = []
   for ipo in ipos:
      if ipo.HistoricalIPO.company_id not in bsym:
         miss.append(ipo.Company.symbol)
   return miss

def checkIPOStartTime(strtime):

   ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 

   for ipo in ipos:
       fttimestr = ipo.HistoricalIPO.first_trade_time
       if fttimestr=="" or fttimestr=="N/A":
          #print "no start time", ipo.Company.symbol, fttimestr
          continue
       fttime = time.strptime(fttimestr, '%H:%M:%S.%f')
       if fttime< time.strptime(strtime, '%H:%M:%S.%f'):
          print ipo.Company.symbol, fttimestr

def compareIPOVol(times):
   ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 

   for ipo in ipos:
      if ipo.HistoricalIPO.first_opening_price == 0.0:
           continue
      pips  = PostIPOPrice.query.filter(PostIPOPrice.company_id ==ipo.HistoricalIPO.company_id).all()
      if len(pips) < 2:
          continue
      ipovol = pips[0].volume
      totalvol = 0
      for pip in pips:
          totalvol += pip.volume
      totalvol -= ipovol
      avevol = totalvol/(len(pips)-1)
      if(ipovol < times * avevol):
          print ipo.Company.symbol, ipovol, avevol 

       


def comparePrice(delta, detail=False):
   his = HistoricalIPO.query.all()
   olist = []
   hlist = []
   llist = []
   clist = []
   for hi in his:
      if hi.first_opening_price == 0.0:
          continue
      pips  = PostIPOPrice.query.filter(PostIPOPrice.company_id ==hi.company_id).filter(PostIPOPrice.date == hi.ipo_date).all()
      if len(pips) ==0:
          continue
      else: 
            od = hi.first_opening_price/ pips[0].open 
            hd = hi.first_day_high/ pips[0].high 
            ld = hi.first_day_low/ pips[0].low 
            cd = hi.first_closing_price/ pips[0].close 
            if od > 1+delta or od < 1-delta:
                    olist.append({"symbol": hi.company.symbol, "tick": hi.first_opening_price, "bar": pips[0].open, "diff": od})
            if hd > 1+delta or hd < 1-delta:
               hlist.append({"symbol": hi.company.symbol, "tick": hi.first_day_high, "bar": pips[0].high, "diff": hd})
            if ld > 1+delta or ld < 1-delta:
               llist.append({"symbol": hi.company.symbol, "tick": hi.first_day_low, "bar": pips[0].low, "diff": ld})
            if cd > 1+delta or cd < 1-delta:
               clist.append({"symbol": hi.company.symbol, "tick": hi.first_closing_price, "bar": pips[0].close, "diff": cd})

   print len(olist), "symbols have inconsistent open price"
   if detail:
        for o in olist:
            print o["symbol"], ":", o["tick"], o["bar"], o["diff"]
   print len(hlist), "symbols have inconsistent high price"
   if detail:
        for o in hlist:
            print o["symbol"], ":", o["tick"], o["bar"], o["diff"]
   print len(llist), "symbols have inconsistent low price"
   if detail:
        for o in llist:
            print o["symbol"], ":", o["tick"], o["bar"], o["diff"]
   print len(clist), "symbols have inconsistent close price"
   if detail:
        for o in clist:
            print o["symbol"], ":", o["tick"], o["bar"], o["diff"]


#compareIPOVol(3)
#checkIPOStartTime("09:30:00.0")
print "num of rows in company table:", len(Company.query.all())
print "num of rows in ipo_url table:", len(IPOInfoUrl.query.all())
print "num of rows in historical table:", len(HistoricalIPO.query.all())

eilist = listExpiredIPOSym();
print len(eilist),"symbols were found in ipo_url but not in company and historical_ipo table. They can either be ETF, or withdrew, or never actually IPOed:", eilist

s0, s1, s2 = diffTickDB()      
print len(s0), 'fetched symbols are not in historical_ipo table:', s0
print len(s1), 'historical ipo symbols were not fetched because they are ealier than 20100701:', s1
print len(s2), 'historical ipo symbols were not fetched for unknown reason:', s2

miss = diffIPOBar()
print len(miss), "cannot get bar data after IPO:", miss
comparePrice(0, detail=True)
