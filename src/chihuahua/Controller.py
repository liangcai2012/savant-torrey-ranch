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
        mod = request["mod"]
        cmd = request["cmd"]
        if mod == "view":
            if cmd == "list":
                # get the list of items in Queue
            elif cmd == "view":
                # view item in the Queue
            elif cmd == "move":
                # re-allocate item in the Queue
            else:
                # remove item in the Queue
        elif mod == "str":
            if cmd == "run":
                # start Strategy instance
            elif cmd == "list":
                # list running strategies
            else:
                # stop running strategy


    def exit(self):
        "Exiting Controller"
        sys.exit(0)

if __name__ == "__main__":
    server = ThreadedServer(Controller,port=8088)
    print "Starting Controller"
    server.start()
