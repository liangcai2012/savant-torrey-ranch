### the server ###

import socket,select
import Queue
from threading import Thread
from time import sleep
from random import randint
import sys


class ProcessThread(Thread):
    def __init__(self):
        super(ProcessThread, self).__init__()
        self.running = True
        self.q = Queue.Queue()
 
    def add(self, data): ## add data into the  queue
        self.q.put(data)
 
    def stop(self):
        self.running = False
 
    def run(self):
        q = self.q
        while self.running:
            try:
                # block for 1 second only:
                value = q.get(block=True, timeout=1)
                process(value)
            except Queue.Empty:
                sys.stdout.write('.')
                sys.stdout.flush()
        #
        if not q.empty():
            print "Elements left in the queue:"
            while not q.empty():
                print q.get()
 
t = ProcessThread()
t.start()
 
def process(value):
    """
    Implement this. Do something useful with the received data.
    """
    print "received client's request:",value
#     sleep(randint(1,9))    # emulating processing time
 
def main():
    s = socket.socket()      
    port = 8090           
    s.bind(("localhost", port))        # Bind to the port
    print "Listening on port {p}...".format(p=port)
 
    s.listen(5)                 # Now wait for client connection.
    while True:
        try:
            client, addr = s.accept()
            ready = select.select([client,],[], [],2)
            if ready[0]:
                data = client.recv(1024)
                #print data
                t.add(data)
        except KeyboardInterrupt:
            print
            print "Stop."
            break
        except socket.error, msg:
            print "Socket error! %s" % msg
            break
    #
    cleanup()
 
def cleanup():
    t.stop()
    t.join()
 
#########################################################
 
if __name__ == "__main__":
    main()
