from json import loads,dumps 
import socket
import time


def test():
    command_add1=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'1s','pos':0,'price':'h','movingave':['1m','5m'],'volume':'y'})
    command_add2=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'1s','pos':0,'price':'l','movingave':['1m','5m'],'volume':'y'})
    command_add3=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'5s','pos':0,'price':'l','movingave':['1m','5m'],'volume':'y'})
    command_add4=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'h','interval':'1s','pos':0,'price':'l','movingave':['1m','5m'],'volume':'y','start':'2015-01-01 09:00:00','end':'2015-01-01 15:00:00'})
    
    command_list=dumps({'cmd':'list'})
    command_mv=dumps({'cmd':'mv', 'id':0,'pos':1})
    command_del=dumps({'cmd':'del', 'id':0,'pos':0})
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
    client.connect(("localhost", 8091))
    client.send(command_add1)
    print 'send add1'
    time.sleep(10)
    client.send(command_add2)
    print 'send add2'
    time.sleep(10)
#     client.send(command_add3)
#     print 'send add3'
#     time.sleep(1)
#     client.send(command_list)
#     time.sleep(2)
#     client.send(command_mv)
#     time.sleep(5)
#     client.send(command_list)
#     time.sleep(2)
#     client.send(command_del)
#     time.sleep(5)
#     client.send(command_list)
    




if __name__ == "__main__":
    test()

