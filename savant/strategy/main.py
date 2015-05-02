import logging
import time
import os
import sys
import brokerageAccount
import PositionManger
import strategies

#et = ETrade.ETrade();
ba = brokerageAccount.BrokerageAccount()
#et.placeOrder
r = dir(strategies)
print(r)

class TStrategyRunner:
    def __init__(self, symbollist, parameters):
        self.__fields_executionContext = ("symbol", "BrokerageAccount", "parameters")
        self.__states = {0:"init", \
                         1:"buy stage", \
                         # 2: buy order is filled, and buy stage is not completed yet
                          2:"buy and sell stage", \
                         # 3:buy stage is completed
                         3:"Sell stage",\
                         4:"postion closed"}
        self.__BrokerageAccount=brokerageAccount.BrokerageAccount()
        self.__PositionManger = PositionManger.PositionManger(symbollist)
        self.__openStrategies= dict()
        self.__closeStrategies= dict()
        self.__executionContext = dict()
        self.__executionContext["Version"] = "1.00"
        self.__executionContext["BrokerageAccount"] = self.__BrokerageAccount
        self.__executionContext["parameters"] = parameters
        getObject_opensName = sys.argv[1] + ".getObject"
        getObject_closesName = sys.argv[2] + ".getObject"
        for s in symbollist:
            func_geObj  = strategies.getMFunctionByName("strategies", getObject_opensName)
            openStrategy= func_geObj()
            func_geObj  = strategies.getMFunctionByName("strategies", getObject_closesName)
            closeStrategy=  func_geObj()
            self.__openStrategies[s] =openStrategy
            self.__closeStrategies[s]=closeStrategy


        self.__currentState = 0
        self.__dutycycleTime = 5 #s
        self.__fields= ("Strategy id", "symbol", "postions")

    def show(self):
        print(self.__states)
    def run_s0(self):
        self.__openStrategy.init(self.__BrokerageAccount)
        result = self.__openStrategy.run(0)
        if(result[0] == "completed"):
            pass
        pass
    def run_s1(slef):
        self.__openStrategy.run(1)
        pass
    def run_s2(slef):
        self.__openStrategy.run(1)
        self.__closeStrategy.run(1)
        pass
    def run_s4(slef):
        self.__closeStrategy.run(4)
        pass
    def run_s5(slef):
        pass
    def run_updatePositionRecords(self,record):
        currentStage = record["currentStage"]
        if(currentStage == 0):
            record["currentStage"] = 1
        pass
    def poocessAPositionRecord(self, symbol, record):
        self.__executionContext["symbol"] =symbol
        currentStage = record["currentStage"]
        openStrategy = self.__openStrategies[symbol]
        closeStrategy = self.__closeStrategies[symbol]
        if(currentStage == 0):
            openStrategy.init(self.__executionContext)
            closeStrategy.init(self.__executionContext)
        elif(currentStage == 1):
            openStrategy.run(currentStage)
        elif(currentStage == 2):
            openStrategy.run(currentStage)
            closeStrategy.run(currentStage)
        elif(currentStage == 3):
            closeStrategy.run(currentStage)
        pass
        pass
    def run(self):
        doRun = True
        cycles=0
        while(doRun):
            cycles = cycles +1
            startT = time.time()
            rs = self.__PositionManger.getPositionRecords()
            for s in rs:
                record = rs[s]

                self.poocessAPositionRecord(s, record)

                self.run_updatePositionRecords(record)
            endT = time.time()
            elapsedT = endT - startT
            if(elapsedT < self.__dutycycleTime):
                time.sleep(self.__dutycycleTime -elapsedT)
        print("strategy done")

m = strategies.getMFunctionByName("strategies", "ShowSysInfo")
m = strategies.getMFunctionByName("strategies", "sclose.getObject")
strategies.ShowSysInfo()
symbols=["spy", "gpro", "yelp"]
parameters = (0.98, 0.95, 1000)
tStrategy = TStrategyRunner(symbols, parameters)
tStrategy.show()
tStrategy.run()
print("done")
