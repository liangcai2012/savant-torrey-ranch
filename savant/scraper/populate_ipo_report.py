from savant.db.models import IPOInfoUrl, HistoricalIPO, Company, Underwriter, CompanyUnderwriterAssociation, PostIPOPrice
from savant.config import settings
from savant.db.models import Exchange, Sector, Industry


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

def getAllTicks():
   
   with open('./list', 'r+') as f:
      symfilelist=f.read().split('\n')[:-1]
      print len(symfilelist)
   symlist = getHistorySym()
   print len(symlist)
   s=[]
   for sf in symfilelist:
      if sf not in symlist:
         print sf
      if sf in s:
         print sf
      else:
         s.append(sf)


def comparePrice():
   his = HistoricalIPO.query.all()
   for hi in his:
      if hi.first_opening_price == 0.0:
          continue
      pips  = PostIPOPrice.query.filter(PostIPOPrice.company_id ==hi.company_id).filter(PostIPOPrice.date == hi.ipo_date).all()
      if len(pips) ==0:
          print hi.company.symbol, " no bar data found"
      else: 
          if (hi.first_opening_price != pips[0].open) or \
               (hi.first_closing_price != pips[0].close) or \
               (hi.first_day_high != pips[0].high) or \
               (hi.first_day_low != pips[0].low):
               print hi.company.symbol, "(",hi.first_opening_price, hi.first_closing_price, hi.first_day_high, hi.first_day_low,") : (", pips[0].open, pips[0].close, pips[0].high, pips[0].low, ")"
               
      
      

comparePrice()
#getAllTicks()      
#print len(listReplicatedIPOSym())
#print len(listExpiredIPOSym()),"symbols were found in ipo_url but not in company and historical_ipo table. They can either be ETF, or withdrew, or never actually IPOed!"
#print listExpiredIPOSym()
#print len(listDuplicatedSym())
