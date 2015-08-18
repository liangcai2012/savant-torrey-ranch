import savant.scraper
import cjson
import savant.fetcher.fetch_attick as fetcher
from savant.db import session
from savant.db.models import *
from savant.ticker.processors import *
from savant.config import settings
import time


def remove_invalid_sym():
   valid=savant.scraper.get_symbols("NYSE")
   valid += savant.scraper.get_symbols("NASDAQ")
   comps = Company.query.filter(~Company.symbol.in_(valid)).all()
   invalid_id = [x.id for x in comps]
   invalid_symbol = [x.symbol for x in comps]
   #print len(invalid_symbol)
   #iius = IPOInfoUrl.query.filter(IPOInfoUrl.symbol.in_(invalid_symbol)).all()
   if len(invalid_symbol) == 0:
      return
   his = HistoricalIPO.query.filter(HistoricalIPO.company_id.in_(invalid_id)).all()
   ticker = TickDataProcessor()
   for hi in his:
      datestr = hi.ipo_date.strftime('%Y%m%d')
      try:
        #remove them from tick data
        paths = ticker.get_ticks_paths_by_date(hi.company.symbol, datestr)
        for path in paths:
            if path != "":
                 os.remove(path)
      except OSError:
        print "cannot find the file", path 

   HistoricalIPO.query.filter(HistoricalIPO.company_id.in_(invalid_id)).delete(synchronize_session='fetch')
   session.commit()
   IPOInfoUrl.query.filter(IPOInfoUrl.symbol.in_(invalid_symbol)).delete(synchronize_session='fetch')
   session.commit()
   CompanyUnderwriterAssociation.query.filter(CompanyUnderwriterAssociation.company_id.in_(invalid_id)).delete(synchronize_session='fetch')
   session.commit()
   PostIPOPrice.query.filter(PostIPOPrice.company_id.in_(invalid_id)).delete(synchronize_session='fetch')
   session.commit()
   Company.query.filter(Company.id.in_(invalid_id)).delete(synchronize_session='fetch')
   session.commit()


def update_split_info():
   split_ipo = [{"symbol": 'HMST', "split": 4.0, "date": ''},
                        {"symbol": 'SFBS', "split": 9.0, "date": ''},
                        {"symbol": 'UBIC', "split": 0.1, "date": ''},
                        {"symbol": 'SFUN', "split": 5.0, "date": ''},
                        {"symbol": 'VIPS', "split": 10.0, "date": '20141104'}] 
   pass

def patch_ipo_date():
   wrong_ipo = { 'HHC': '20101105', 
                     'CHKR': '20111111',
                     'NLNK': '20111111',
                     'WLH': '20130118',
                     'RTRX': '20121108',
                     'RXDX': '20140129',
                     'VGGL': '',
                     'FCAU': '20100609',
                     'BLMT': '20111005',
                     'XELB': ''}

   res  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).filter(Company.symbol.in_(wrong_ipo.keys())).all() 
   tickdata_dir = settings.DOWNLOAD_DIR
   ticker = TickDataProcessor()
   for r in res:
       symbol = r.Company.symbol
       id = r.Company.id
       #remove them from tick data
       datestr = r.HistoricalIPO.ipo_date.strftime('%Y%m%d')
       try:
          paths = ticker.get_ticks_paths_by_date(r.Company.symbol, datestr)
          for path in paths:
             if path != "":
                os.remove(path)
       except OSError:
          print "cannot find the file", path 
       if wrong_ipo[symbol] == "":
            # remove the data and remove the symbol from ipo related tables as this is not an actual IPO, might be SPO
            HistoricalIPO.query.filter(HistoricalIPO.company_id == id).delete(synchronize_session='fetch')
            session.commit()
            IPOInfoUrl.query.filter(IPOInfoUrl.symbol==symbol).delete(synchronize_session='fetch')
            session.commit()
            PostIPOPrice.query.filter(PostIPOPrice.company_id==id).delete(synchronize_session='fetch')
            session.commit()
       else:
            hi = HistoricalIPO.query.filter(HistoricalIPO.company_id == id).first()
            hi.ipo_date=datetime.strptime(wrong_ipo[symbol], '%Y%m%d').date()

            session.commit()
#fetch data
            ipo_data_dir = os.path.join(tickdata_dir, wrong_ipo[symbol])
            ipo_data_path = os.path.join(ipo_data_dir, "%s_markethours.csv.gz" % symbol)
            if os.path.exists(ipo_data_dir) and os.path.exists(ipo_data_path):
                print "IPO data found"
            else:
                request = {"command": "get", "symbol": symbol, "date": wrong_ipo[symbol]}
                print request
                print cjson.encode(request)
                fetcher_caller = fetcher.FetcherCaller()
                fetcher_caller.set_request(cjson.encode(request))
                try:
                    response = fetcher_caller.send_request()
                    fetcher_caller.close()
                except:
                    print "Unable to send fetch request"
                    continue
   
                count_down = 60
                fetched = False
                while count_down > 0:
                    if os.path.exists(ipo_data_path):
                        print "IPO data fetched:", symbol
                        fetched = True
                        time.sleep(5)
                        break
                    time.sleep(1)
                    count_down -= 1
                if not fetched:
                    print "Unable to download data for", symbol


   #his = savant.db.models.HistoricalIPO.query.filter(HistoricalIPO.company.symbol in wrong_ipo.keys()).all()
   #for hi in his:
   #   hi.ipo_date = wrong_ipo[hi.company.symbol].strftime("%Y%m%d")
   #   savant.db.session.commit()

#remove_invalid_sym()
patch_ipo_date()
