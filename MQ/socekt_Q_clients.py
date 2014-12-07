# client.py
 
import sys
import socket

input= "abcdefg"


def main(elems):
    try:
        for e in elems:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            client.connect(("localhost", 8090))
            client.send(e)
            client.shutdown(socket.SHUT_RDWR)
            client.close()
    except Exception as msg:
        print msg
 
#########################################################
 
if __name__ == "__main__":
    main(input)