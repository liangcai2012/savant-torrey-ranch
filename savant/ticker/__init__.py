
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
