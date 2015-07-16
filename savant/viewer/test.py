from json import loads,dumps 
import socket
import time


def test():
    command_add11=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'1s','pos':0,'price':'h','movingave':['1m','5m'],'volume':'y'})
    command_add12=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'1s','pos':0,'price':'l','movingave':['1s','5s','1m','5m'],'volume':'y'})
    command_add13=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'1s','pos':0,'price':'o','movingave':['1m','5m'],'volume':'y'})
    command_add14=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'1s','pos':0,'price':'c','movingave':['1m','5m'],'volume':'y'})
    command_add15=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'5s','pos':0,'price':'c','movingave':['1m','5m'],'volume':'y'})
    command_add16=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'10s','pos':0,'price':'c','movingave':['1m','5m'],'volume':'y'})
    
    command_add3=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'r','interval':'5s','pos':0,'price':'l','movingave':['1m','5m'],'volume':'y'})
    command_add4=dumps({'cmd':'add', 'symbol':'QQQ', 'type':'h','interval':'1s','pos':0,'price':'l','movingave':['1m','5m'],'volume':'y','start':'2015-01-01 09:00:00','end':'2015-01-01 15:00:00'})
    
    command_list=dumps({'cmd':'list'})
    command_mv=dumps({'cmd':'mv', 'id':0,'pos':1})
    command_del=dumps({'cmd':'del', 'id':0,'pos':0})
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
    client.connect(("localhost", 8091))
    client.send(command_add11)
    print 'send add11'
    time.sleep(5)
    client.send(command_add12)
    print 'send add12'
    time.sleep(7)
    client.send(command_add13)
    print 'send add13'
    time.sleep(9)
    client.send(command_add14)
    print 'send add14'
    time.sleep(12)
    client.send(command_add15)
    print 'send add15'
    time.sleep(15)
    client.send(command_add16)
    print 'send add16'
    time.sleep(5)
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

