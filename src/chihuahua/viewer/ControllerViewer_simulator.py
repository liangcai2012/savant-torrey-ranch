import sys
import rpyc
from rpyc.utils.server import ThreadedServer
from time import sleep

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
                print "get the list of items in Queue"
            elif cmd == "view":
                print "view item in the Queue"
                toViewer = rpyc.connect('localhost', 8090, config={'allow_public_attrs': True})
                cmd_show={"cmd":"show", "sym":"QQQ", "interval": "1"}
                toViewer.root.show(cmd_show)
                
            elif cmd == "move":
                print "re-allocate item in the Queue"
            else:
                print "remove item in the Queue"
        elif mod == "str":
            if cmd == "run":
                print "start Strategy instance"
            elif cmd == "list":
                print "list running strategie"
            else:
                print " stop running strategy"


    def exit(self):
        "Exiting Controller"
        sys.exit(0)

if __name__ == "__main__":
#     server = ThreadedServer(Controller,port=8088)
#     print "Starting Controller"
#     server.start()

    ###### for simulator with Viewer########
    toViewer = rpyc.connect('localhost', 8090, config={'allow_public_attrs': True})
    cmd_show1={"cmd":"show", "sym":"QQQ", "interval": "1"}
    cmd_show2={"cmd":"show", "sym":"SPY", "interval": "1"}
    cmd_list={"cmd":"list"}
    
    toViewer.root.show(cmd_show1)
    sleep(1)       
    list=toViewer.root.list(cmd_list) 
    print list 
#     toViewer.root.show(cmd_show2)             
                
                
    
