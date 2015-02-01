import StrategyBase
class Trigger:
     def __init__(self,openPrice, percentage):
         self.__openPrice = openPrice
         self.__percentage = percentage
         self.__eventTrigged = False
     def run(self, currentprice):
        p = currentprice /self.__openPrice
        if(p <= self.__percentage):
            self.__eventTrigged = true
        return self.__eventTrigged

     def eventTrigged(self):
         return self.__eventTrigged




class StrategyOpen(StrategyBase.StrategyBase):
    def __init__(self):
        # action: none, completed,  buy, short
        # the last paramter is the number of shares to buy if condition meet
        self.__symbol = None
        self.__brokerageAccount = None
        self.__parameters = None #(0.98, 0.95, 1000)
        self.__openprice = 0

        self.__fields = ("action","symbol",  "shares", "price")
    def init(self,executionContext):
        #, symbol, brokerageAccount, parameters
        #pass
        self.__cycleCount = 0
        self.__executionContext = executionContext
        brokerageAccount = executionContext["BrokerageAccount"]
        self.__symbol= executionContext["symbol"]
        openPrice = brokerageAccount.getOpenPrice(self.__symbol)
        parameters = executionContext["parameters"]


        self.__Trigger1 = Trigger( openPrice,parameters[0] )
        self.__Trigger2 = Trigger( openPrice,parameters[1] )
    def CheckTrigger(self, ask, trigger):
        # Do ckecking only the trigger has not been trigered.
        if(trigger.eventTrigged()== False):
            if(trigger.run(ask)):
                self.__brokerageAccount.placeMarketOrder(self.__symbol, "buy",self.__parameters[2] )
    def run(self, stage):
        brokerageAccount = self.__executionContext["BrokerageAccount"]
        quote = brokerageAccount.getQuote(self.__symbol)
        ask = quote[1]
        curPrice = brokerageAccount.getOpenPrice(self.__symbol)
        # all the two event have been triggered,
        #return "done" to indicate the strategy is done.
        if(self.__Trigger1.eventTrigged() or self.__Trigger1.eventTrigged()):
            return ["done"]

        self.CheckTrigger(ask,self.__Trigger1 )
        self.CheckTrigger(ask,self.__Trigger2 )


        msg = "running stage #%s: %s %s" %(str(stage), self.__symbol, str(self.__cycleCount))

        print(msg)
        self.__cycleCount = self.__cycleCount +1
        return ["continue"]
        pass

def getObject():
    obj = StrategyOpen()
    return obj
