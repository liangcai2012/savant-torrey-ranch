#! /usr/bin/env python
import cProfile
import time
import rpyc
import sys
import locale
import platform
import testcase
def FormatInt(v):
    strSystem = platform.system()
    if ("Linux" in strSystem):
        locale.setlocale(locale.LC_ALL, 'en_US')
    elif ("Windows" in strSystem):
        locale.setlocale(locale.LC_ALL, "english")
    r = locale.format("%d", v, grouping=True)
    #print(r)
    return r
v = sys.version
#host = "192.168.0.30"
#host = "172.16.1.78"
host="localhost"
print("==== python version info ====")
print (v)
conn = rpyc.connect(host, 8000)
def writeData(data):
    name = 'log.txt'
    file = open(name, 'w')
    file.write(str(data))
def test_getgetResult():
    t0= time.time()
    conn.root.echo("hello world2")
    r = conn.root.getResult()
    if(testcase.testcase==1):
        msg = "RPC function return " + str(r)
        print(msg)
    elif(testcase.testcase==3 or testcase.testcase==4):
        t= (time.time() - t0)
        size = len(r)
        speed = size / t
        speed2 = int(speed)
        size_str= FormatInt(size)
        
        msg = "number of bytes received = " + size_str
        print(msg)    
        speed_str= FormatInt(speed2)
      
        msg = "tranfter speed[bytes per second] = " + speed_str
        print(msg)
    #print(speed, t)
    
def main():    
    # conn.root.print_time()
    conn.root.echo("hello world2")
    r = conn.root.add(1,2)
    print(r)
    r = conn.root.getResult()
    #print("size received", len(r))
    #r = conn.root.getResult()
    #print("size received", len(r))
    #r = conn.root.getResult()
    #print("size received", len(r))
    #input("done...")
msg = "==== Test result ===="
print(msg)
test_getgetResult()
#test_getgetResult()
input("done...")
#cProfile.run('main()')

