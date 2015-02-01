import socket
# from jsonrpc import loads,dumps
from json import loads,dumps 
from time import sleep
import sys


json = {"method":"getTickData","params":["AAPL"],"id":"req-01","jsonrpc":"2.0"}
req = dumps(json)
# req="Hello from client\n"
req=req+"\n"
print req
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("localhost",8080))

sock.send(req)

sock.settimeout(2)
## Not receiving response from Java server
resp = sock.recv(4096) #bufsize
poscl = resp.replace("\x00(","")
sock.close()
#respST =loads(resp)
print "We got the fb from server: " 
print repr(poscl) 


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
