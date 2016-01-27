from savant.db.models import * 
from savant.db import session
from savant.config import settings
from savant.ticker.processors import *

#Tick2SecondBarConverter('WLRHU', "20140606")
#exit(0)


ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
for ipo in ipos:
    symbol = ipo.Company.symbol
    date = str(ipo.HistoricalIPO.ipo_date).replace('-', '')
    tick_gz_path = settings.DATA_HOME + '/data/' + date + '/' + symbol + '_markethours.csv.gz'
    bar_gz_path = settings.DATA_HOME+ '/data/' + date + '/' +symbol + '_second_bar.csv.gz' 
    if os.path.exists(tick_gz_path) and not os.path.exists(bar_gz_path):
        print  ipo.Company.symbol, str(ipo.HistoricalIPO.ipo_date).replace("-", "")
        Tick2SecondBarConverter(ipo.Company.symbol, str(ipo.HistoricalIPO.ipo_date).replace('-', ''))
