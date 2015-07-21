import sqlite3
import numpy as np
import matplotlib.pyplot as plt


def filter_openPrice(times, year):
	conn = sqlite3.connect('../../../out/savant.db')
	c = conn.cursor()
	day1 = year+'-01-01 00:00:00:000'
	lastday = year+'-12-31 23:00:00:000'
	str1="SELECT c.symbol FROM company AS c INNER JOIN historical_ipo AS h ON c.id = h.company_id WHERE (first_opening_price> (price*?) AND price!=0 AND h.ipo_date > ? AND h.ipo_date < ?);" 
	c.execute(str1,(times, day1, lastday)) 
	symbollist=c.fetchall()
	conn.close()
	return symbollist 
	
if __name__ == "__main__":
	steps = [0, 5, 10, 20, 30, 50, 100, 1000]
	dist = []
	print 'year, total ipo, ',
	for s in steps:
		print '<'+str(1+s/100.0)+',',
	print ''
	years = range(2010, 2016)
	for y in years:
		d = []
		totalnum = len(filter_openPrice(0.1, str(y)))
		d.append(totalnum)
		print str(y),
		print totalnum, 
		hnum = totalnum
		for s in steps:
			num = len(filter_openPrice(1+s/100.0, str(y)))
			r = (hnum-num)*1.0/totalnum
			d.append(r)
			print "{:.2f}".format(r), 
			hnum = num
		print ''
		dist.append(d)
