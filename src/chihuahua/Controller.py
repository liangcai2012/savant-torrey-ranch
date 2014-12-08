from Strategy import *

class Controller:

    def __init__(self,lstStrat):
	self.lstStrat = set(lstStrat)
   
    def invokeWorker(self):
	stratGenerator = StrategyGenerator().generate(self.lstStrat)
	for worker in stratGenerator:
	    if worker != None:
	  	worker.start()
 	

if __name__ == "__main__":
    c = Controller(["simple","simple"])
    c.invokeWorker()
