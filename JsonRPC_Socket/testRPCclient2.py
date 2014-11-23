import socket
# from jsonrpc import loads,dumps
from json import * 
from time import sleep
import sys


json = {"method":"getTickData","params":["FB"],"id":"req-02","jsonrpc":"2.0"}
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
print "We got the feedback from server: " 
print repr(poscl) 

