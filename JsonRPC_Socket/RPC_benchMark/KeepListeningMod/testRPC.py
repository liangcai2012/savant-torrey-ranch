import socket
# from jsonrpc import loads,dumps
from json import loads,dumps 
from time import sleep
import sys,datetime


json = {"method":"getTickData","params":["AAPL"],"id":"req-01","jsonrpc":"2.0"}

# req = dumps(json)
# req="Hello from client\n"
# req="ads"
# req=req+"\n"
# print req
data=""

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("localhost",8080))  # to java's accept()
# sock.send(req)


sock.settimeout(2)
## Not receiving response from Java server
ts=datetime.datetime.now()

for i in range(1024):
#     sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#     sock.connect(("localhost",8080))
    req = dumps(json)
    req=req+"\n"
    sock.send(req) ;
    resp = sock.recv(50) #bufsize
    if not resp: break
#     sock.close()
#     print repr(resp) 
#     poscl = resp.replace("\x00(","")
#     data+=resp
elapsed_time=datetime.datetime.now()-ts

# sock.close()
# respST =loads(resp)
print "We got the fb from server: " 
# print repr(resp) 
# print len(resp)*i
print sys.getsizeof(data)
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
