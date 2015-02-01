#import caiss.sysinfo
class BrokerageAccount:
    def getQuote(self, symbol):
        bid = 200.0
        ask = 200.1
        bidSize = 100
        askSize = 200
        data = (bid, ask,bidSize, askSize )
        return data
    # possible action value: buy , sell
    def placeMarketOrder(self, symbol, action, shares):
        pass
    def placeOrder4(self, symbol, action, price, shares):
        pass
    def getOpenPrice(self, symbol):
        openp = 20
        return openp
    def placeOrder(self, dictOrder):
        pass
    def getAvailableMargin(self):
        pass
    def getOrderObjectTemplate(self, symbol):
        order = {"symbol":symbol, "action":"buy Or Sell", "price":0.0, "shares":1000}
        return order


if __name__ == "__main__":
    ba = BrokerageAccount()
    q= ba.getQuote("spy")
    o = ba.getOrderObjectTEmplate("spy");
    o2 = ba.getOrderObjectTEmplate("spy");
    keys = o.keys();
    keys2 = o2.keys();
    #caiss.sysinfo.showinfo(keys)
    if(keys == keys2):
        print("same keys'")
    print(o)
    print(keys)
    print(q)