import socket,select 
import heapq 
import bisect
import datetime 
import time
import sqlite3

from savant.config import settings
from savant.fetcher.fetch_attick0 import *

def get_data(symbol,date):
    request = {"command":"get","symbol":symbol,"date":date}
    json_request = json.dumps(request)
    caller = FetcherCaller(json_request) 

def check_status():
    request = {"command":"check"}
    json_request = json.dumps(request)
    caller = FetcherCaller(json_request) 
    return caller.stat

def show_intervals(ds):
    s=''
    ind=0
    for i in ds:
        if ind%2==0:
            if ind>0:
                s+=' '
            s+='['
        s+=str(daynum2date(i))
        if ind%2!=0:
            s+=')'
        else:
            s+=' '    
        ind+=1
    return s

def load_intervals(curs,symbol): 
    
    param=(symbol,) 
    curs.execute("select map from symbolmap where symbol=?",param) 
    dr= curs.fetchone() 
    
    if not dr:# or dr[0]=='':
        return [],False
    
    ds=dr[0].split(',') #csv string to list 
    ds=map(int,ds)
    '''
    ds=[]#['1','5','7','11'] 
    if dict.has_key(symbol):
        ds=dict[symbol].split(',')
        ds=map(int,ds) # ds = [int(i) for i in ds] 
    '''
    return ds,True 

def save_intervals(curs,symbol,itvs):
    
    ds=map(str,itvs[0])
    dr=','.join(s for s in ds)
    
    if itvs[1]:
        param=(dr,symbol,)
        curs.execute("update symbolmap set map=? where symbol=?",param)
    else:
        param=(symbol,dr,)
        curs.execute("insert into symbolmap values(?,?)",param)
    conn.commit()
    '''
    dict[symbol]=dr
    '''

    return dr

def search_or_insert_intervals(itv,v,flag):
    ind = bisect.bisect(itv,v) # ind to insert
    found= ind%2==1 #existing
    if not found and flag: #insert
        if(ind<len(itv) and v+1==itv[ind]):
            itv.remove(v+1)
        else:
            itv.insert(ind,v+1)
        if(-1<ind-1 and v==itv[ind-1]):
            itv.remove(v)
        else:
            itv.insert(ind,v)    
    return found

def load_queue(fn): 
    pq= [] 
    file = open(fn) 
    for line in file.readlines(): 
        tp=[] 
        ind=0; 
        for i in line.strip().split(','): 
            if ind<3: 
                tp.append(int(i)) 
            else: 
                tp.append(i) 
            ind+=1 
        pq.append(tp)     
    file.close() 
    heapq.heapify(pq) 
    return pq     

def save_queue(fn,pq): 
    file = open(fn,'w') 
    for line in pq: 
        file.write(','.join(str(s) for s in line) + '\n') 
    file.close() 
    return 

def daynum2date(dn): 
    d0=datetime.date(1980,1,1) 
    d1=d0+datetime.timedelta(days=dn)
    s=d1.strftime('%Y-%m-%d')
    return s

def secnum2time(sn):
    t0=datetime.datetime(1980,1,1,0,0,0)
    t1=t0+datetime.timedelta(seconds=sn)
    s=t1.strftime('%Y-%m-%d_%H:%M:%S')
    return s

def dump_queue(pq): 
    res="" 
    for line in pq:
        res+=str(-line[0])+','
        res+=secnum2time(line[1])+','
        res+=daynum2date(line[2])+','
        res+=line[3]+'\n'
    return res 

def date2daynum(ds): 
    d0=datetime.date(1980,1,1) 
    dt=ds.split('-') 
    d1=datetime.date(int(dt[0]),int(dt[1]),int(dt[2])) 
    return (d1-d0).days 

def time2secnum(t1):
    t0=datetime.datetime(1980,1,1,0,0,0)
    return int((t1-t0).total_seconds())

def fill_queue(tp,pq): 
    rank=-(int)(tp[4])
    toprank=False
    if rank>0:
        if len(pq)==0:
            rank=0
        else:
            rank=pq[0][0]-1      
        toprank=True
    symbol=tp[1] 
    reqtime=time2secnum(datetime.datetime.now())
    ds=date2daynum(tp[2]) 
    de=date2daynum(tp[3]) 
    for day in range(ds,de+1): 
        heapq.heappush(pq,[rank,reqtime,day,symbol]) 
    return toprank

def timestamp():
    return datetime.datetime.now().strftime('%H:%M:%S')

''' # UNIT TESTS
ds=load_intervals(1,1)
found=search_or_insert_intervals(ds,6,True)
ss=show_intervals(ds)
dd=save_intervals(1,1,ds)
'''

#ds=load_intervals(1,1)

'''
dict = {'AAPL': '1,5,7,11', 'BL': '2,4'};
curs=1
'''
conn = sqlite3.connect("map.db")
curs=conn.cursor()



pq= load_queue("queue.txt") 
host=""; 
port=50000; 

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
s.bind((host,port)); 
s.listen(8); 

toprank=False

while 1:
    toprank=False 
    infds,outfds,errfds = select.select([s,],[],[],0.1) 
    if len(infds) != 0: 
        clientsock,clientaddr = s.accept() 
        buf = clientsock.recv(8196) 
        
        if len(buf) != 0: 
            print "- command coming"
            print (buf) 
            tp=buf.strip().split(' ') 
            if tp[0]== "get": 
                toprank=fill_queue(tp,pq) 
                if not toprank:
                    clientsock.send("queued") 
            elif tp[0]=="where": 
                itvs=load_intervals(curs,tp[1])
                clientsock.send(show_intervals(itvs[0]))
            elif tp[0]=="queue": 
                clientsock.send(dump_queue(pq)) 
            elif tp[0]=="end": 
                clientsock.send("end request") 
                #clientsock.close() 
                break
        if not toprank:
            clientsock.close() 
    #print "- task processing"
    res=""
    if len(pq)==0:
        res= "no task in queue. "+timestamp()
    else:
        qf=heapq.heappop(pq)
        itvs=load_intervals(curs,qf[3])
        found=search_or_insert_intervals(itvs[0],qf[2],True)
        if found:
            res=qf[3]+' '+daynum2date(qf[2])+' '+"already existed!"
        else:
            save_intervals(curs,qf[3],itvs)
            dat=daynum2date(qf[2])
            res="fetching: RANK "+str(-qf[0])+' '+qf[3]+' '+dat#daynum2date(qf[2])
            
            sym=qf[3]
            dat=dat.replace('-','')
            get_data(sym,dat)
            while 1:
                stat=check_status()
                if stat.find('Idle')>-1:
                    break
                else:
                    print 'not idle! '+timestamp()
                time.sleep(4)     
            #time.sleep(4) # fetching    
    print res
    if toprank:
        clientsock.send(res)
        clientsock.close() 

curs.close()
conn.close() 

save_queue("queue.txt",pq) 