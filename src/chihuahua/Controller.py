from Strategy import *

class Controller:

    def __init__(self,strategy_list):
	self.strategy_list = set(strategy_list)
   
    def invokeWorker(self):
	stratGenerator = StrategyGenerator()
	for strat in self.strategy_list:
	    worker = stratGenerator.generate(strat)
	    if worker != None:
		worker.start()
 	

if __name__ == "__main__":
    c = Controller(["simple","simple"])
    c.invokeWorker()
