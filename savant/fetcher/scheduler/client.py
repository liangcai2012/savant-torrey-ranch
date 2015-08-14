import socket,select 
import sys

host = "localhost" 
port = 50000 

#while 1:
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.connect((host,port)) 
#print "input command: "
line = sys.stdin.readline()
#if not line:
#    break
# Print the line read.
#sl= line[:-1]
#print sl
s.send(line)#sl)
#s.send("get AAPL 2015-01-01 2015-01-06 5") 
#s.send("get AAPL 2015-01-01 2015-01-06 -1") 
buf=s.recv(8196) 
print buf
#if sl=="end":
#    break 
s.close() 