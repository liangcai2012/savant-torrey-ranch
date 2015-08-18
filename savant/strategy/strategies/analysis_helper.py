from savant.db.models import * 
from savant.db import session
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy
from savant.utils.ploty import *

def scoop_openratio_assoc():
	ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
	data = []
	for ipo in ipos:
		if ipo.HistoricalIPO.first_opening_price == 0:
			continue
		if ipo.HistoricalIPO.scoop_rating == 'N/A':
			continue
		if ipo.HistoricalIPO.price > 1:
			ratio = ipo.HistoricalIPO.first_opening_price/ipo.HistoricalIPO.price 
			data.append({"symbol": ipo.Company.symbol, "price_rate": ratio, "scoop_rate": ipo.HistoricalIPO.scoop_rating}) 
	print data
	
	fig = plt.Figure()
	fig, axes = plt.subplots()
	#fig.add_subplot(111)
	#axes = fig.gca()
#	display_distribution(axes, data, "price_rate",  0.2)
	display_association(axes, data, "price_rate", "scoop_rate")
	plt.show()

def open_price_dist():
	ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
	data = []
	max_ratio = 0
	max_symbol = ""
	for ipo in ipos:
		if ipo.HistoricalIPO.first_opening_price == 0:
			continue
		if ipo.HistoricalIPO.scoop_rating == 'N/A':
			continue
		if ipo.HistoricalIPO.price > 1:
			ratio = ipo.HistoricalIPO.first_opening_price/ipo.HistoricalIPO.price 
			data.append({"symbol": ipo.Company.symbol, "price_rate": ratio, "scoop_rate": ipo.HistoricalIPO.scoop_rating}) 
			if ratio >max_ratio:
				max_ratio = ratio 
				max_symbol = ipo.Company.symbol
			if ratio < 0.8:
				print ipo.Company.symbol, ipo.Company.id, ratio 
	
	print max_symbol, max_ratio
	span=numpy.arange(1,4,0.2)
	
	fig = plt.Figure()
	fig, axes = plt.subplots()
	#fig.add_subplot(111)
	#axes = fig.gca()
	display_distribution(axes, data, "price_rate",  0.2)
	plt.show()


scoop_openratio_assoc();

