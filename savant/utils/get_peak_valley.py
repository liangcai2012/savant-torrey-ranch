import os
import savant.ticker.processors as processors
import pandas as pd
import time
from savant.config import settings
from savant.db.models import * 
from savant.db import session
import savant.utils.ploty as ploty
import matplotlib.pyplot as plt
import numpy as np
import pylab as P

def get_peak_valley(symbol, date, range_list, price_type):
    if len(range_list)==0:
        print "invalid range list:", range_list
        return None
    range_list.sort()
    if range_list[0] <= 0: 
        print "invalid range:", range_list
        return None

    bar_gz_path = settings.DATA_HOME+ '/data/' +  date + '/' +symbol+"_second_bar.csv.gz" 
    if not os.path.exists(bar_gz_path):
        print "second bar data does not exist:", bar_gz_path
        return None

    bar_pd = processors.bar2pd(bar_gz_path)
    #print bar_pd["open"][0]
    #print (bar_pd.index[1]-bar_pd.index[0]).total_seconds()
    open = bar_pd["open"][0]
    open_vol = bar_pd["volume"][0]

    peak_list = []
    ptime_list = []
    valley_list = []
    vtime_list = []
    ind = 0
    last_ind = 0
    peak = 0
    valley = 1000000000
    for r in range_list: 
        while (bar_pd.index[ind]-bar_pd.index[0]).total_seconds() < r:
            if bar_pd[price_type][ind] > peak:
                peak = bar_pd[price_type][ind]
                peak_time = (bar_pd.index[ind]-bar_pd.index[0]).total_seconds() 
            if bar_pd[price_type][ind] < valley:
                valley = bar_pd[price_type][ind]
                valley_time = (bar_pd.index[ind]-bar_pd.index[0]).total_seconds()
            ind += 1

        peak_list.append(peak)
        ptime_list.append(peak_time)

        valley_list.append(valley)
        vtime_list.append(valley_time)

#we probably also need more data: ipo_date, total shared, offered share, first vol, industry, sector,  
    return [open_vol, open, peak_list, ptime_list, valley_list, vtime_list]


def flat_result(res):
    str = ""
    for i in range(len(res[0])):
        str += "{0:.0f}".format(res[1][i])
        str += ', '
        str += "{0:.2f}".format(res[0][i])
        str += ', '
    for i in range(len(res[0])):
        str += "{0:.0f}".format(res[3][i])
        str += ', '
        str += "{0:.2f}".format(res[2][i])
        str += ', '
    return str[:-2]


def get_all_ipo_pv():
    ipos  = session.query(Company, HistoricalIPO).filter(Company.id == HistoricalIPO.company_id).all() 
    outfile = open(settings.DATA_HOME+"/ipo_pv.csv", 'w')
    
    for ipo in ipos:
#    print  ipo.Company.symbol, str(ipo.HistoricalIPO.ipo_date).replace("-", "")
        sym = ipo.Company.symbol
        ipo_date = str(ipo.HistoricalIPO.ipo_date).replace('-','')
        scoop_rate = ipo.HistoricalIPO.scoop_rating
        ipo_price = ipo.HistoricalIPO.price
        ipo_open_price = ipo.HistoricalIPO.first_opening_price
        shares = ipo.HistoricalIPO.shares
        outstanding = ipo.HistoricalIPO.outstanding
        try:
            sector = ipo.Company.sector.name.replace(',', ';')
        except AttributeError:
            sector = ""

        try:
            industry = ipo.Company.industry.name.replace(',', ':')
        except AttributeError:
            industry = ""
            

        print sym, ipo_date 
        bar_gz_path = settings.DATA_HOME+ '/data/' +  ipo_date + '/' +sym+"_second_bar.csv.gz" 
        if not os.path.exists(bar_gz_path):
            tick_gz_path = settings.DATA_HOME+"/data/"+ipo_date+"/"+sym+"_markethours.csv.gz"
            if not os.path.exists(tick_gz_path):
                print "no tick data found"
                continue
            processors.Tick2SecondBarConverter(sym, ipo_date)
            print "generated second bar for", sym
        res = get_peak_valley(sym, ipo_date, [60, 180, 300, 600], "open")
        if res == None:
            print "cannot get peak and valley data for", sym
            continue
        outfile.write(sym + ", " + ipo_date + ', ' + str(scoop_rate) + ', ' +
                    sector + ', ' + industry + ', ' +
                    str(shares) + ', ' + str(outstanding) + ', ' +
                    str(ipo_price) + ', ' + str(res[0]) + ', ' + str(res[1]) +', ' +
                    flat_result(res[2:]) + '\n')

    outfile.close()


def load_pv():
    pv_path= settings.DATA_HOME+ '/ipo_pv.csv' 
    if not os.path.exists(pv_path):
        print "pv file does not exist"
        return

    pv_pd = pd.read_csv(pv_path, names=["sym", "ipodate", "scoop", "sector", "industry", "shares", "outstanding", "pricing", "open_vol", "open",  "pt1", "p1", "pt2", "p2", "pt3", "p3", "pt4", "p4", "vt1", "v1", "vt2", "v2", "vt3", "v3", "vt4", "v4"], index_col=[0])
    return pv_pd


def draw_histo(data, bar):
    P.figure()
    n, bins, patches = P.hist(data , bar, histtype='step')
    P.show()


def plot_peak_percentage_by_scoop():
    pv_pd = load_pv()
    pv_iter = pv_pd.iterrows()
    list= [[],[],[],[],[]]
    for i, row in pv_iter:
        peak_10m = max(row["p1"], row["p2"], row["p3"], row["p4"])
        percentage = int(peak_10m*100/row["open"])
        try:
            scoop = int(row["scoop"])
        except:
            scoop = 0
        list[scoop].append(percentage)
    #most are in 100-120, max 153.3
    bar_peak_percentage = range(100,121) + [160]
    print [np.histogram(list[i], bar_peak_percentage)[0][0] for i in range(len(list))]
    print [np.histogram(list[i], bar_peak_percentage)[0][1] for i in range(len(list))]
    print [np.histogram(list[i], bar_peak_percentage)[0][2] for i in range(len(list))]
    draw_histo(list, bar_peak_percentage)
    return list 
    
def plot_open_percentage_by_scoop():
    pv_pd = load_pv()
    pv_iter = pv_pd.iterrows()
    list= [[],[],[],[],[]]
    for i, row in pv_iter:
        if row['pricing']==0:
            print i, 'has zero ipo price in database'
            continue
        percentage = int(row["open"]*100/row['pricing'])
        try:
            scoop = int(row["scoop"])
        except:
            scoop = 0
        list[scoop].append(percentage)

    #from 70-250
    bar_open_percentage = range(70, 250, 10)
    draw_histo(list, bar_open_percentage)
    return 

def find_mini_cap_ipo():
    pv_pd = load_pv()
    pv_iter = pv_pd.iterrows()
    list= [[], []]
    for i, row in pv_iter:
        if row['pricing']==0:
            print i, 'has zero ipo price in database'
            continue
        shares = int(row["shares"])
        
        if row["pricing"]*shares < 50000000:
            print i, row["ipodate"], row['open_vol'], row['shares'], row['outstanding'], row['scoop'], row['pricing'], row["open"], row['sector'], row['industry']
    return 

def plot_open_vol_dist():
    pv_pd = load_pv()
    pv_iter = pv_pd.iterrows()
    list= []
    for i, row in pv_iter:

        try:
            if row["open_vol"] > float(row['shares']):
                print 'impossible', i, row['open_vol'], row['shares']
            list.append(row['open_vol']/float(row['shares']))
        except ValueError:
            print i, row['open_vol'], row['shares']
            
    print sum(list)/float(len(list)) 
    draw_histo(list, 11)
    return list

def plot_two_percentage():
    pv_pd = load_pv()
    pv_iter = pv_pd.iterrows()
    list= [[], []]
    for i, row in pv_iter:
        if row['pricing']==0:
            print i, 'has zero ipo price in database'
            continue
        try:
            shares = float(row['shares'])
            if row["open_vol"] > shares: 
                continue
        except ValueError:
            print i, 'does not have shares info' 
            continue

        if row['open_vol']/shares > 0.25:
            peak_10m = max(row["p1"], row["p2"], row["p3"], row["p4"])
            if peak_10m/row["open"] > 1.01:
                continue
        #if (peak_10m/row["open"] <1.0005) and  (row['open']/row["pricing"] > 1.3): 
#        list.append([peak_10m*/row["open"], int(row["open"]*100/row['pricing'])])
            print i, row["ipodate"], row['open_vol'], row['shares'], row['outstanding'], row['scoop'], row['pricing'], row["open"], peak_10m, row['sector'], row['industry']
            list[0].append(peak_10m/row["open"])
            list[1].append(row["open"]*100.0/row['pricing'])
    print len(list[0])
    #print np.histogram(list[1], range(70, 250, 10)) 
    #plt.plot(list[0], list[1], '.')
    #plt.show()
    return 

def boost_by_openvol(pv_pd, boost_percentage, openvol_percentage):
    pv_iter = pv_pd.iterrows()
    nTotal = 0
    nFiltered = 0
    for i, row in pv_iter:
        try:
            shares = float(row['shares'])
            if row["open_vol"] > shares: 
                continue
        except ValueError:
            continue


        if row['open_vol']/shares > openvol_percentage:
            nTotal += 1
            peak_10m = max(row["p1"], row["p2"], row["p3"], row["p4"])
            if peak_10m/row["open"] > 1+  boost_percentage:
                continue
            nFiltered += 1

    return [nTotal, nFiltered]

def plot_boost_percentage():
    pv_pd = load_pv()
    for bp in [0, 0.5, 1, 1.5, 2]:
        bp = (bp+1)/100.0
        list=[[], []]
        print '-----bp =', bp, '------'
        for i in range(20):
            res = boost_by_openvol(pv_pd, bp, i/20.0)
            if res[0] > 5 :
                list[0].append(i/20.0)
                list[1].append(float(res[1])/res[0])
                print list[0][-1], res[1], res[0], "{0:.2f}".format(list[1][-1]) 
        #print list[0], list[1]
        #plt.plot(list[0], list[1])
    #plt.show()
    return

    


def test():
    print get_peak_valley("CYAD", "20120724", [60, 180, 300, 600], "open")

if __name__ == "__main__":
    #plot_boost_percentage()

    #plot_peak_percentage_by_scoop()
    #plot_open_percentage_by_scoop()
    #find_mini_cap_ipo()
#    plot_two_percentage()
    #plot_open_vol_dist()
    #print list
    #[len(list[i]) for i in range(len(list))]
    

#    get_all_ipo_pv()
    processors.Tick2SecondBarConverter("MB", "20150619")
    #test()

        

