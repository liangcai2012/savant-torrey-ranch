import pandas as pd
# import sqlite3

def rate_finder(sym):
    header_row=['date','name','symbol','underwriter','a','b','c','d','e','f','rate','meet']
    data=pd.read_csv('../../../out/iposcoop.csv' , header=None, names=header_row)

    df=pd.DataFrame(data)
    # print data
    temp= pd.DataFrame(df.loc[df['symbol']==(sym)])
    temp.date=pd.to_datetime(temp.date)

    result=temp.sort('date')[-1:]['rate'] #sort by date->get last raw->get rate
#   print  type(result)
    print "The rate of '%s' is:" %sym, result.iloc[0]  #get item from pandas series   
    
    
if __name__ == "__main__":
    rate_finder('BOX')













