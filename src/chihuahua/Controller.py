import sys
import rpyc
from rpyc.utils.server import ThreadedServer

class Controller(rpyc.Service):

    def invokeWorker(self):
        for strat in self.lstStrat:
            try:
		mod = __import__("strategy" + strat)
                stratCls = getattr(getattr(mod,strat),strat)
                stratCls().start()
            except:
                print "Strategy class " + strat + " doesn't exist!"

    def exposed_request(self,request):
        print request

    def exposed_exit(self):
        "Exiting Controller"
        sys.exit(0)

if __name__ == "__main__":
    server = ThreadedServer(Controller,port=8088)
    print "Starting Controller"
    server.start()
