import os
import subprocess
import pandas as pd
import datetime as dt
from savant.config import settings

base_dir = settings.DOWNLOAD_DIR

# stock data type: ticks, bars.  
# ticks have three basic sub type of ticks: trades, quotes and quote_changes.  quote_changes is a derived data from quotes
tick_type = ["trade", "quote", "quote_change"]

#columes:
trade_col = ["datetime", "price", "size", "exch", "cond"]
quote_col = ["datetime", "bidprice", "askprice", "bidsize", "asksize", "bidexch", "askexch", "cond"]
quote_ch_col = ["datetime", "side", "newprice", "pricechange", "newsize", "sizechange", "exch", "cond"] 
bar_col = ["datetime", "open", "high", "low", "close", "volume"] 

#trade_tick, quote_tick, second_bar and min_bar are pre-fected and stored in file system
trade_csv_col = ["datetime", "type", "price", "size", "exch", "cond"]
quote_csv_col = ["datetime", "type", "bidprice", "askprice", "bidsize", "asksize", "bidexch", "askexch", "cond"]
second_bar_csv_col = ["datetime", "open", "high", "low", "close", "volume", "average"] 
minute_bar_csv_col = bar_col 

# all stock data use dt(datetime) as index, tick and bar has different format
tick_date_parser = lambda x: pd.datetime.strptime(x+"000", '%m/%d/%Y %H:%M:%S.%f')
bar_date_parser = lambda x: pd.datetime.strptime(x, '%Y%m%d%H%M%S')


def _get_trade_tick_suffix(hours):
    if hours == "regular":
        suffix = ["_markethours"]
    elif hours == "pre":
        suffix = ["_premarket"]
    elif hours == "after":
        suffix = ["_aftermarket"]
    elif hours == "full":
        suffix = ["_premarket", "_markethours", "_aftermarket"]
    else:
        raise ValueError("No such hours: %s" % hours)
    return suffix

def _get_quote_tick_suffix():
    return "_quote"


# return a list of four paths: pre, markethour, after, quotes
#This function is to replace get_ticks_paths_by_date() in Processor. It returns quote path as well
def get_ticks_paths_by_date(symbol, date):
    paths=[]
    suffix_list = _get_trade_tick_suffix("full")
    for suffix in suffix_list:
        filename = symbol + suffix + ".csv.gz" 
        trade_path = os.path.join(base_dir, date, filename)
        if not os.path.exists(trade_path):
           paths.append("")
        else:
           paths.append(trade_path)
    filename = symbol + _get_quote_tick_suffix() + ".csv.gz" 
    quote_path = os.path.join(base_dir, date, filename)
    if not os.path.exists(quote_path):
        paths.append("")
    else:
        paths.append(quote_path)
    return paths


#get trade ticks by multiple dates
#this is to replace get_ticks_by_date
def get_trades_by_date(symbol, date, hours="regular"):
    suffix = _get_trade_tick_suffix(hours)
    filenames = [symbol + s + ".csv.gz" for s in suffix]
    #print filenames
    tick_data = None 
    for filename in filenames:
        data_path = os.path.join(base_dir, date, filename)
        if not os.path.exists(data_path):
            #print "cannot find", data_path
            continue
            #raise IOException("Data file not found: %s" % data_path)
        cur_ticks = pd.read_csv(data_path, compression="gzip", names= trade_csv_col, usecols = trade_col, parse_dates=[0], date_parser=tick_date_parser, index_col=0)
        if tick_data is None:
            tick_data = cur_ticks
        else:
            tick_data = pd.concat([tick_data, cur_ticks])
    return tick_data

def get_quotes_by_date(symbol, date):
    suffix = _get_quote_tick_suffix()
    filename = symbol + suffix + ".csv.gz"
    data_path = os.path.join(base_dir, date, filename)
    if not os.path.exists(data_path):
        print "cannot find", data_path
        return None
    tick_data = pd.read_csv(data_path, compression="gzip", names= quote_csv_col, usecols =quote_col, parse_dates=[0], date_parser=tick_date_parser, index_col=0)
    return tick_data


def get_secondbar_by_date(symbol, date): 
    bar_gz_path = settings.DATA_HOME+ '/data/' +  date + '/' +symbol+"_second_bar.csv.gz" 
    if not os.path.exists(bar_gz_path):
        print "second bar data does not exist:", bar_gz_path
        return None

    bar_pd = pd.read_csv(bar_gz_path, compression="gzip", names = second_bar_csv_col, usecols = bar_col,  index_col=[0], parse_dates=[0], date_parser=bar_date_parser)
    return bar_pd

#the input tick data frame can be trades or quotes, but it has to be date_parsed  
def filter_ticks_by_datetime(tick_df,  begin_datetime, end_datetime):
    if not isinstance(begin_datetime, dt.datetime) or not isinstance(end_datetime, dt.datetime) or begin_datetime >= end_datetime:

        raise ValueError("Invalid datetime")
    df_iter = tick_df.iterrows()
    bfound = False
    b = None 
    e = None 
    for i, row in df_iter:
        if not bfound: 
            if i< begin_datetime:
                continue
            else:
                b = i
                bfound = True
        else:
            if i>end_datetime:
                break
            else:
                e = i
                continue
    if b is None or e is None:
        return None

    return tick_df[b:e] 

#this can be used for trade ticks or quote_changes 
def filter_ticks_by_exchange(tick_df, exchange):
    return tick_df[tick_df["exch"]==exchange]

#we will implement this later. So far all secondbar are stored and only needs to be read out 
#downsampling arbitrary dataframe? tick data is not processed to removed dual opening etc. maybe not a good idea
def tradetick_to_secondbar(trade_df):
    pass

#this is to replace Tick2SecondBarConverter
def generate_secondbar_from_tradetick(symbol, date):
    bar_path = settings.DATA_HOME+ '/data/' + date + '/' +symbol+"_second_bar.csv" 
    bar_gz_path = bar_path+".gz" 
    if os.path.exists(bar_gz_path):
        return

    tickdata = get_trades_by_date(symbol, date, "full")
    if tickdata is None:
        print "trade data cannot be found, exiting second bar conversion"
        return

    try:
        fbar = open(bar_path, 'w')
    except IOError:
        return

    begin_time = None
    tick_batch = []
    current_dt = None

    cond_9= False
    cond_15 = False
    for i, tick in tickdata.iterrows():
        #handle conditions
        #assumption: conditions cannot contain both 9 and 15 or 16
        #9 might be followed by 15 or 16
        #any record before 16 is not valid

        condlist = tick["cond"].split('-')
        for cond in condlist:
            if cond == '9' or cond == "15" or cond == "16":
                break
        if cond == '9':
            cond_9 = True 
            prev_vol = tick["size"] 
        elif cond == '16':
            if cond_9 and tick["size"] == prev_vol:
# do not remove the second bars before open, try to be literate as the tick data
#                if len(tick_batch)>1:
#                    print symbol, date, "contains trade records before offical open!"
#                tick_batch=[]
                cond_9 = False
                continue
        elif cond == "15":
            if cond_9 and tick["size"] == prev_vol:
                cond_9 = False
                continue
        else:
            if cond_9:
                cond_9 = False

        #time_no_ms = tick[1][0].split('.')[0]# remove the millisecond part
        #tick_dt = datetime.datetime.strptime(time_no_ms, '%m/%d/%Y %H:%M:%S')
        if current_dt == None:
            #current_dt = tick_dt
            current_dt = i.replace(microsecond = 0) 
        #if (tick_dt - current_dt).seconds < 1:
        if (i - current_dt).seconds < 1:
            tick_batch.append(tick) 
            continue
        else: #tick_dt >= self.current_dt
            if len(tick_batch)>0:
                p_open, p_close, p_high, p_low, volume, p_average = _calc_bar_from_tick_batch(tick_batch)
                if p_open != None:
                    fbar.write(current_dt.strftime("%Y%m%d%H%M%S") + ", " + str(p_open) + ", " + str(p_high) + ", "+ str(p_low) + ", " + str(p_close) + ", " + str(volume) + ", " + p_average + '\n')

            while(i - current_dt).seconds >= 1:
                current_dt += dt.timedelta(0, 1)
            tick_batch=[tick]
    fbar.close()
    subprocess.check_call(["gzip", bar_path])

#internal function only used by the generate_secondbar_from_tradetick
def _calc_bar_from_tick_batch(ticks):
    trade_prices= [t["price"] for t in ticks]
    po = trade_prices[0]
    pc = trade_prices[-1]
    ph = max(trade_prices)
    pl = min(trade_prices)
    vol = sum([t["size"] for t in ticks])
    #there are chances that tick record with vol = 0
    if vol == 0:
        return None, None, None, None, None, None
    trade_cost = sum([t["price"]*t["size"] for t in ticks])
    pave = format(trade_cost/vol, ".2f")
    return po, pc, ph, pl, vol, pave 


#return the records only when there is a change in price or size
def get_quote_change(quote_df):
    cur_ask_price = cur_bid_price = 0.0
    cur_ask_size = cur_bid_size = 0
    cur_ask_exch = cur_bid_exch = None
    dict_index = []
    dict_data = []
    num = 0
    q_iter = quote_df.iterrows()
    for i, row in q_iter:
        bidchanged = askchanged = False
        if (row["askprice"] == 0.0) or (row["bidprice"] == 0.0):
            if row["askprice"]!= 0.0 or row["bidprice"]!= 0.0:
                print "one side of bid/ask is zero"
            continue
        if (cur_ask_price != row["askprice"]) or (cur_ask_size != row["asksize"]):
            askchanged = True
            dict_index.append(i)
            dict_data.append(["ask", row["askprice"], row["askprice"]-cur_ask_price, int(row["asksize"]), int(row["asksize"]-cur_ask_size), int(row["askexch"]), int(row["cond"])])
            cur_ask_price = row["askprice"]
            cur_ask_size = row["asksize"]
        if (cur_bid_price != row["bidprice"]) or (cur_bid_size != row["bidsize"]):
            dict_index.append(i)
            dict_data.append([ "bid", row["bidprice"], row["bidprice"]-cur_bid_price, int(row["bidsize"]), int(row["bidsize"]-cur_bid_size), int(row["bidexch"]), int(row["cond"])])
            cur_bid_price = row["bidprice"]
            cur_bid_size = row["bidsize"]
    quote_ch_tick = pd.DataFrame(dict_data, index=dict_index, columns = quote_ch_col[1:]) 
    return quote_ch_tick
    
def bid_change_only(quote_ch_df):
    return quote_ch_df[quote_ch_df["side"]=="bid"]

def ask_change_only(quote_ch_df):
    return quote_ch_df[quote_ch_df["side"]=="ask"]

def down_sample_secondbar(bar_pd):
    pass

def print_df(df, sep="\t"):
    print df.to_csv(sep=sep)

def calc_time_diff(timeOne, timeTwo, millisec=False):
    """
    Calculate difference in times in sec.
    """
    try:
        ts1 =  timeOne.split(".")
        ts2 =  timeTwo.split(".")
        c1 = ts1[0]
        c2 = ts2[0]
        
        h1, m1, s1 = [int(i) for i in c1.split(":")]
        h2, m2, s2 = [int(i) for i in c2.split(":")]
        if millisec:
            ms1=ts1[1]
            ms2=ts2[1]
            return (h2-h1)*3600 + (m2-m1)*60 + (s2-s1) + (int(ms2)-int(ms1))/1000
        else:
            return (h2-h1)*3600 + (m2-m1)*60 + (s2-s1)
    except Exception, e:
        print e
        raise ValueError("The times given are invalid")

def datetime_to_timestamp(datetime_str):
    datetime_no_ms = datetime_str.split('.')[0]  # remove the millisecond part
    try:
        t = dt.datetime.strptime(datetime_no_ms, '%m/%d/%Y %H:%M:%S')
        return t.strftime('%Y%m%d%H%M%S')
    except ValueError:
        return None

def test_trade():
    trade_df = get_trades_by_date("GPRO", "20140626", "full") 
    #dt_last = trade_df.index[-1]
    #print trade_df.loc[dt_last]
    start = dt.datetime.strptime("20140626105030", '%Y%m%d%H%M%S')
    end = dt.datetime.strptime("20140626105041", '%Y%m%d%H%M%S')
    #trade_df_filtered = filter_ticks_by_datetime(trade_df, start, end)
    trade_df_filtered = filter_ticks_by_exchange(trade_df, 81)
    print trade_df_filtered
    #print trade_df

def test():
    #testing generate_secondbar_from_tradetick
    generate_secondbar_from_tradetick("TUMI", "20120419")

    ##test get_quotes_by_date
    #quote_df = get_quotes_by_date("GPRO", "20140626")
    ##print quote_df
    #quote_ch_df = get_quote_change(quote_df)
    #print_df(bid_change_only(quote_ch_df))

