import sqlite3

def filter_openPrice(x):
    conn = sqlite3.connect('savant.db')
    c = conn.cursor()
    times=x
    str1="SELECT symbol FROM company WHERE id in (SELECT company_id FROM historical_ipo WHERE (first_opening_price> (price*%s) AND price!=0 ) );" %times
    symbollist=c.fetchall()
    print symbollist 
    
if __name__ == "__main__":
    filter_openPrice(20)


