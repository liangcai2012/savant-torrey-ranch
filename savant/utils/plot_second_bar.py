import os
import savant.ticker.processors as processors
import savant.dataAPI as dataAPI
import pandas as pd
import time
import savant.highcharts.core as pdhc
from savant.config import settings

def barpd2hc(bar_pd, chart_title, pricetype, showvolume, htmlfile):

     #<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    html1='''
<!DOCTYPE html>
<html>
  <head>
    <script type="text/javascript" src="../lib/highstock/jquery.min.js"></script>
    <style type="text/css">
            ${demo.css}
    </style>
    <script  type="text/javascript">
  $(function(){ 
       $('#mychart').highcharts('StockChart',
       '''
    html2 = ''' ); 
    });
    </script> 
    <title>Flarx</title>
  </head>
  <body>
    <script src="../lib/highstock/js/highstock.js"></script>
    <script src="../lib/highstock/js/modules/exporting.js"></script>
    <div id="mychart"></div>
 </body> </html> 
'''
    if showvolume:
        chart = pdhc.serialize(bar_pd[[pricetype, "volume"]], render_to="mychart", title=chart_title, secondary_y=["volume"] ) 
    else:
        chart = pdhc.serialize(bar_pd[[pricetype]], render_to="mychart", title=chart_title) 

    html_path = settings.DATA_HOME+"/" + htmlfile
    fhtml = open(html_path, 'w')
    fhtml.write(html1+chart+'\n'+ html2)
    fhtml.close()
    return 

def plot_secondly_bar(symbol, date, title = None, price_type = "open", display_volume = True, volume_downscale = False, htmlfile="index.html"):
    if price_type != "open" and price_type != "close" and price_type != "high" and price_type!= "low":
        print "Invalid price type"
        exit()
    bar_gz_path = settings.DATA_HOME+ '/data/' +  date + '/' +symbol+"_second_bar.csv.gz" 
    if not os.path.exists(bar_gz_path):
        print "Generating second bar date..."
        processors.Tick2SecondBarConverter(symbol, date)
        #tick2bar(symbol, date, bar_path)
    bar_pd = processors.bar2pd(bar_gz_path)
    if volume_downscale:
        bar_pd.is_copy=False
        bar_pd.iloc[0, -1] /=100
    barpd2hc(bar_pd, symbol+': ' + date, price_type, display_volume, htmlfile)
    print "Chart is ready, run 'open ../out/index.html' to view the chart"

if __name__ == "__main__":
    plot_secondly_bar("GPRO", "20140626", volume_downscale=True)

###############Not used#################
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

def test():
    sym = "GPRO"
    date = "20140626"
    #sym = "NTRA"
    #date = "20150702"
    barpath = sym+date+"_sec_bar.csv.gz"
    #tick2bar(sym, date, barpath)
    bar_pd = processors.bar2pd(barpath)
    starttime = time.time()
    barpd2hc(bar_pd)
#tick_pd = tick2pd(sym, date)
#print tick_pd.count()
#dateparse = lambda x: pd.datetime.strptime(x+"000", '%m/%d/%Y %H:%M:%S.%f')
#print time.time() - starttime, " seconds to parse the tick data"
###############################################

