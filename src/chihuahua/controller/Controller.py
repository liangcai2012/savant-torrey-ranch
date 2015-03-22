import sys
import rpyc
from rpyc.utils.server import ThreadedServer

class Controller(rpyc.Service):

    def exposed_request(self,request):
        print request
        mod = request["mod"]
        del request["mod"]
        if mod == "view":
            conn = rpyc.connect("localhost", 8090, config={"allow_public_attrs": True})
            conn.root.request(request)
        elif mod == "str":
            pass

    def exit(self):
        "Exiting Controller"
        sys.exit(0)

if __name__ == "__main__":
    server = ThreadedServer(Controller,port=8088)
    print "Starting Controller"
    server.start()
