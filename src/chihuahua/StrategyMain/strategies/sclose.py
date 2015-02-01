import StrategyBase
class Strategyclose(StrategyBase.StrategyBase):
    def __init__(self):
        # action: none, completed,  buy, short
        self.__fields = ("action","symbol",  "shares", "price")
    #def init(self,brokerageAccount, parameters):
    def init(self,executionContext):
        #, symbol, brokerageAccount, parameters
        pass
    def run(self, stage):
        print(stage)
        pass

def getObject():
    obj = Strategyclose()
    #obj.init(brokerageAccount, parameters)
    return obj

if __name__ == "__main__":
    getObject().run(1)
