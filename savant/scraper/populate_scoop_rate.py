import pandas as pd
from savant.config import settings
from savant.db.models import * 
from savant.db import session
# import sqlite3

def rate_finder(sym):
    header_row=['date','name','symbol','underwriter','a','b','c','d','e','f','rate','meet']
    data=pd.read_csv(settings.DATA_HOME+'/iposcoop.csv' , header=None, names=header_row)

    df=pd.DataFrame(data)
    # print data
    temp= pd.DataFrame(df.loc[df['symbol']==(sym)])
    if len(temp) == 0:
        return None
    temp.date=pd.to_datetime(temp.date)

    result=temp.sort('date')[-1:]['rate'] #sort by date->get last raw->get rate
#   print  type(result) return result.iloc[0]
    #print "The rate of '%s' is:" %sym, result.iloc[0]  #get item from pandas series   
    return result.iloc[0]
    

def update_scoop_rate():
    ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
    for ipo in ipos:
        sym = ipo.Company.symbol
        rate = rate_finder(sym)
        if rate == None:
            continue
        hi = HistoricalIPO.query.filter(HistoricalIPO.company_id == ipo.Company.id).first()
        if hi == None:
            continue #should not happen
        hi.scoop_rating = rate
    session.commit()    



if __name__ == "__main__":
   update_scoop_rate()
   # rate_finder('ABCW')













