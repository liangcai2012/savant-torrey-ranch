#  APPF 2015-06-26
import pandas as pd
import datetime
import savant.ticker as ticker
import savant.ticker.processors as processors
import matplotlib.pyplot as plt



tick_proc = processors.TickDataProcessor()



tics = tick_proc.get_ticks("APPF", "20150626", "20150626", parse_dates=True)
# tics



begin_time = tics.iloc[0].name
end_time = tics.iloc[-1].name
rng = pd.date_range(begin_time, end_time, freq='S')
counts_per_sec = pd.DataFrame(0, index= rng,columns =['count' ])



for ind, tic in tics.iterrows():
    if tic.price > 0 and tic.size > 0:
        counts_per_sec.ix[ind] += 1




from sklearn import linear_model
class Portfo:
    def __init__(self):
        self.balance = 10000
        self.position = 0
        self.trade = pd.DataFrame(columns=["datetime", "amount", "price", "value"])
    def buy(self, price, time = None):
        if self.position > 0 :
            return False
        else:
            amount = int(self.balance / price)
            self.position += amount
            trade = pd.DataFrame ({"datetime": time, "amount": [amount], "price": [price], "value": [self.balance]})
            self.balance -= amount * price
            self.trade = self.trade.append(trade)
            return True

    def sell(self, price, time = None):
        if self.position <= 0 :
            return False
        else:
            self.balance += self.position * price
            trade = pd.DataFrame ({"datetime": time, "amount": [-self.position], "price": [price], "value": [self.balance]})
            self.trade = self.trade.append(trade)
            self.position = 0
            return True

    def value(self, price):
        return self.balance + self.position * price





po = Portfo()
period = 5
def check_rising(shortics):
    prf = linear_model.LinearRegression()
    shortics = shortics[shortics.price > 0]
    titims = (shortics.index -  shortics.index[0]).seconds.reshape(-1, 1)
    prf.fit(titims, shortics.price.values)
    if prf.coef_[0] <= 0 :
        return False
    if prf.predict([titims[-1]]) > shortics.price.values[-1]:
        return False
    else:
        return True

def check_lowing(shortics):
    prf = linear_model.LinearRegression()
    shortics = shortics[shortics.price > 0]
    titims = (shortics.index -  shortics.index[0]).seconds.reshape(-1, 1)
    prf.fit(titims, shortics.price.values)
    if prf.coef_[0] > 0 :
        return False
    if prf.predict([titims[-1]]) < shortics.price.values[-1]:
        return False
    else:
        return True



for ind, count in counts_per_sec.iterrows():
    prev_sec = ind - datetime.timedelta(seconds = 1)
    prev_secs = counts_per_sec.ix[prev_sec - datetime.timedelta(seconds = period) : prev_sec]
    if prev_sec not in counts_per_sec.index:
        continue
    if len(prev_secs) < period:
        continue
    if 0 not in prev_secs['count'].values:
        x = (prev_secs.index -  prev_secs.index[0]).seconds.reshape(-1, 1)
        res = linear_model.LinearRegression()
        res.fit(x, prev_secs['count'].values)

        check_rising(tics.ix[prev_secs.index])

        if res.coef_[0] < 0:
            continue
        if check_rising(tics.ix[prev_secs.index]):
            po.buy(tics.ix[:ind].ix[-1].price, ind)
        elif check_lowing(tics.ix[prev_secs.index]):
            po.sell(tics.ix[:ind].ix[-1].price, ind)

    prev_secs = counts_per_sec.ix[prev_sec - datetime.timedelta(seconds = 15 * period) : prev_sec]
    if (prev_secs['count'].values == 0).all():
        po.sell(tics.ix[:ind].ix[-1].price, ind)




print len(po.trade)
po.trade


sep = datetime.datetime.strptime('2015-06-26 11:17:02', '%Y-%m-%d %H:%M:%S')
tics.ix[:sep]['price'] .plot()


tics['price'] .plot()


