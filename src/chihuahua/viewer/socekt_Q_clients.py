# client.py
 
import sys
import socket
from json import loads,dumps 


# input_str= "{\"cmd\":\"add\"; {\"sym\":\"xxxx""start\":starttime; \"end\":endtime; \"interval\": numofsec}}"
input_str_add= {"cmd":"add", "sym":"AAPL","start":"0", "end":"0", "interval": "1"}
input_str_list={"cmd":"list"}
input_str_move={"cmd":"move", "id": "id", "position":"position"}
input_str_remove={"cmd":"remove", "id": "id"}

input_add=dumps(input_str_add)
input_list=dumps(input_str_list)
input_move=dumps(input_str_move)
input_remove=dumps(input_str_remove)


def main():
    try:
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
        client.connect(("localhost", 8090))
        client.send(input_add)
#         client.send(input_list)
#         client.send(input_move)
#         client.send(input_remove)
        
        client.shutdown(socket.SHUT_RDWR) #add shutdown before close(): immediately close socket
        client.close()
    except Exception as msg:
        print msg
 
#########################################################
 
if __name__ == "__main__":
    main()