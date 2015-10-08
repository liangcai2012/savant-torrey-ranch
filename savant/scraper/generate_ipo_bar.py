from savant.db.models import * 
from savant.db import session
from savant.config import settings
from savant.ticker.processors import *

ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
for ipo in ipos:
#    print  ipo.Company.symbol, str(ipo.HistoricalIPO.ipo_date).replace("-", "")
    processors.Tick2SecondBarConverter(ipo.Company.symbol, str(ipo.HistoricalIPO.ipo_date).replace('-', ''))

