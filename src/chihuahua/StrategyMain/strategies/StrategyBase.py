class StrategyBase:
    # executionContext is an dictionary with following 4 items
    # "Version": the value is "1.00"
    #"BrokerageAccount": the value is an BrokerageAccount object
    #"parameters": The value is  parameters passed by user
    #"symbol": stock symbol
    def init(self,executionContext):
        raise NotImplementedError()
    def run(self, stage):
        raise NotImplementedError()
