class Controller:

    def __init__(self,lstStrat):
	self.lstStrat = set(lstStrat)
   
    def invokeWorker(self):
        for strat in self.lstStrat:
            try:
	        mod = __import__("strategy." + strat)
                stratCls = getattr(getattr(mod,strat),strat)
                stratCls().start()
            except:
                print "Strategy class " + strat + " doesn't exist!"

if __name__ == "__main__":
    c = Controller(["Simple","Complex"])
    c.invokeWorker()
