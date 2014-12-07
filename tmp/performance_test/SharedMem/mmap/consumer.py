#! /usr/bin/env python3.4
import mmap
import time
import locale
import platform
import sys
r = dir(mmap.mmap)
print(r)
def FormatInt(v):
    strSystem = platform.system()
    if sys.platform.startswith('linux'):
        locale.setlocale(locale.LC_ALL, 'en_US')
    elif sys.platform.startswith('win32'):
        locale.setlocale(locale.LC_ALL, "english")
    r = locale.format("%d", v, grouping=True)
    #print(r)
    return r
def showinfo(obj, doprintobj):
    t = type(obj)
    print(t)
    if(doprintobj):
        print(obj)

# write a simple example file
#with open("hello.txt", "wb") as f:
#    f.write(b"00Hello Python!\n")

with open("/tmp/mm.txt", "r+b") as f:
    # memory-map the file, size 0 means whole file
    mm = mmap.mmap(f.fileno(), 0)
    # read content via standard file methods
    #print(mm.readline())  # prints b"Hello Python!\n"
    # read content via slice notation
    showinfo(mm, False)
    #showinfo(mm[1], True)
    t0= time.time()
    loopcount = 0
    transftercount=0
    maximum_transftercount=10000
    while(True):
        
        loopcount = loopcount +1
#       #(mm[0] == 1 indicates the shared memory is ready to be used.
        if(mm[0] == 1):
            # set mm[0] to 2 to indicate the shared memory is processed..
            mm[0] = 2
            
            
            if(transftercount%1000 == 0):
                s =  FormatInt(loopcount)
                print(transftercount,s )
               
            if(transftercount >= maximum_transftercount):
                break
            transftercount = transftercount +1
            #time.sleep(0.00005)
            #mm.flush()
            #if(transftercount%2 == 0):
                #time.sleep(0.0005)
        #time.sleep(0.0000001)
        time.sleep(0.0002)
       
    # close the map
    #mm.close()
t= (time.time() - t0)
speed = transftercount/t
print("time elapse=", t)
#convert speed to integer
ispeed = int(speed)
print("shared memory transfters per second:" + str(ispeed))
input("done...")
