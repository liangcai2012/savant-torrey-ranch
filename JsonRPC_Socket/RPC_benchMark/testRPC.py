import socket
# from jsonrpc import loads,dumps
from json import loads,dumps 
from time import sleep
import sys,time


json = {"method":"getTickData","params":["AAPL"],"id":"req-01","jsonrpc":"2.0"}

req = dumps(json)
# req="Hello from client\n"
req="\n"
print req
data=""

# sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# sock.connect(("localhost",8080))
# sock.send(req)


# sock.settimeout(2)
## Not receiving response from Java server
ts=time.time()
for i in range(1024):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(("localhost",8080))
    sock.send(req) ;
    resp = sock.recv(1024) #bufsize
#     sock.close()
#     print repr(resp) 
#     poscl = resp.replace("\x00(","")
#     data+=resp
elapsed_time=time.time()-ts

sock.close()
# respST =loads(resp)
print "We got the fb from server: " 
# print repr(data) 
print len(resp)*i
print sys.getsizeof(resp)
print elapsed_time, ts


# 
# while True:
#     try:
#         msg = sock.recv(4096)
#     except socket.error, e:
#         err = e.args[0]
#         if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
#             sleep(1)
#             print 'No data available'
#             continue
#         else:
#             # a "real" error occurred
#             print e
#             sys.exit(1)
#     else:
#          print "ddd" # got a message, do something :)
# 
# print "resp is:"
# sock.close()
