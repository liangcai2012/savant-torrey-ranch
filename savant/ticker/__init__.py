import datetime as dt
class Quote(object):

    __slots__ = ("datetime", "bid", "ask", "bidsize", "asksize", "bidexch", "askexch", "cond")

    def __init__(self, dt, bid, ask, bidsize, asksize, bidexch, askexch, cond):
        self.datetime = dt
        self.bid = bid
        self.ask = ask
        self.bid_size = bidsize
        self.ask_size = asksize
        self.bid_exch = bidexch
        self.ask_exch = askexch
        self.cond = cond

class Trade(object):

    __slots__ = ("datetime", "last", "lastsize", "lastexch", "cond")

    def __init__(self, dt, last, lastsize, lastexch, cond):
        self.datetime = dt
        self.last = last
        self.last_size = lastsize
        self.last_exch = lastexch
        self.cond = cond

def calc_time_diff(timeOne, timeTwo, millisec=False):
    """
    Calculate difference in times in sec.
    """
    try:
        c1, ms1 = timeOne.split(".")
        c2, ms2 = timeTwo.split(".")
        h1, m1, s1 = [int(i) for i in c1.split(":")]
        h2, m2, s2 = [int(i) for i in c2.split(":")]
        if millisec:
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

