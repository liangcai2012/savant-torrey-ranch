import socket
from jsonrpc import loads,dumps

json = {"method":"getTickData","params":["AAPL"],"id":"req-01","jsonrpc":"2.0"}
req = dumps(json)
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("localhost",8080))

sock.send(req)
## Not receiving response from Java server
# resp = sock.recv(1024)
# print resp
sock.close()
