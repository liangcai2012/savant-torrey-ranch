import time
import json
from savant import streamer

sc = streamer.getStreamerCaller()
#print sc.subscribe("test1", ["QCOM", "LOCO", "YELP"])
print sc.subscribe("test2", ["QQQ"])
#print sc.unsubscribe("test1")
#print sc.update("test2", "3s")
#print sc.update("test1", "5s")
while True:
   jret = json.loads(sc.update("test2", "1s"))
   print jret
   st = jret['response']['timestamp']
   bar = jret['response']['data'][0]['bar']   
   if len(bar) != 0:
      print st, bar
   time.sleep(1)
