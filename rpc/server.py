#! /usr/bin/env python3.4
import rpyc
import time
from rpyc.utils.server import ThreadedServer
import reabinfile
import testcase
xrange = range
import sys
v = sys.version
print (v)
def getBiglist():
    biglist = []
    count = 10*1000 * 1000
    for i in range(count):
         biglist.append(i)
def getBigString():
    seed = "0123456789"
    data =""
    count = 10*1000 * 1000
    for i in range(count):
        data += seed
    return data

    print("elements in biglist",len(biglist))
    return biglist
# Valid testcase is 1,2,3.
# change testcase to your desired test case.
#testcase = 2
print(dir(testcase))
if(testcase.testcase==1):
    gdata = [0, 1,2,3,4,5,6,7,8,9]
elif(testcase.testcase==2):
    gdata = getBiglist()
elif(testcase.testcase==3):
     gdata=getBigString()
elif(testcase.testcase==4):
    gdata=reabinfile.getBigFileData()
class TimeService(rpyc.Service):
    def exposed_print_time(self):
        for i in xrange(10):
            print (time.ctime())
            time.sleep(1)
    def exposed_echo(self, msg):
        print("data received",msg)
    def exposed_add(self, a, b):
        return a+b
    def exposed_getResult(self):
        print("data to send", len(gdata))
        #return [1,2,4]
        return gdata

if __name__ == "__main__":
    print("Starting RPCserver")
    t = ThreadedServer(TimeService, port=8000)
    t.start()
    print("RPCserver running")
    #time.sleep(10)
input("press enter to continue...")
