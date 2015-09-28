import savant.ticker.processors as processors
import savant.dataAPI as dataAPI
import pandas as pd
import time
import savant.highcharts.core as pdhc
from savant.config import settings


def tick2pd(sym, date):
    ticker = processors.TickDataProcessor()
    tickdata = ticker.get_ticks_by_date(sym, date, date, hours="regular", parse_dates=True)
    return tickdata

def tick2bar(sym, date, barpath):
    #print tickdata.count
    fw = open(barpath,  'w')
    da = dataAPI.getDataAPI("test")
    if da.subscribeHistory([{"sym":sym, "time": date+"-093000"}]) != 0:
        print "fail to subscribe"
        exit()
    while True:
        ret = da.update("1s")
        if ret == None:
            fw.close()
            break
        fw.write(ret['timestamp'] + ", " + ret['data'][0]['bar'] + '\n')

def bar2pd(barfile):
    dateparse = lambda x: pd.datetime.strptime(x, '%Y%m%d%H%M%S')
    bar_data = pd.DataFrame(columns=["datetime", "open", "high", "low", "close", "volume"])
    bar_pd = pd.read_csv(barpath, names=["datetime", "open", "high", "low", "close", "volume"], index_col=[0], parse_dates=[0], date_parser=dateparse)
    return bar_pd

def barpd2hc(bar_pd):

     #<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    html1='''
<!DOCTYPE html>
<html>
  <head>
     <script type="text/javascript" src="../lib/highstock/jquery.min.js"></script>
    <script src="../lib/highstock/js/highstock.js"></script>
    <script src="../lib/highstock/js/modules/exporting.js"></script>
    <title>Flarx</title>
  </head>
  <body>
    <div id="my-chart"></div>
    <script type="text/javascript">
'''
    
    html2 = ' </script> </body> </html> '

    chart = pdhc.serialize(bar_pd[["open", "volume"]], render_to="mychart", title="test", secondary_y=["volume"] ) 

    html_path = settings.DATA_HOME+"/index.html"
    fhtml = open(html_path, 'w')
    fhtml.write(html1+chart+'\n'+ html2)
    fhtml.close()
    return 


sym = "BABA"
date = "20140919"
#sym = "NTRA"
#date = "20150702"
barpath = sym+date+"_sec_bar.csv"
#tick2bar(sym, date, barpath)
bar_pd = bar2pd(barpath)
starttime = time.time()
barpd2hc(bar_pd)
#tick_pd = tick2pd(sym, date)
#print tick_pd.count()
#dateparse = lambda x: pd.datetime.strptime(x+"000", '%m/%d/%Y %H:%M:%S.%f')


#print time.time() - starttime, " seconds to parse the tick data"
