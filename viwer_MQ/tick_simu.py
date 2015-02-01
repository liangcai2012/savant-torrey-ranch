import pickle
import random
import time,select
import socket
# import pika



class Ticker(object):
    def __init__(self):
#         self.publisher = publisher

        # This quickly creates four random stock symbols
#         chars = range(ord("A"), ord("Z")+1)
#         def random_letter(): return chr(random.choice(chars))
#         self.stock_symbols = [random_letter()+random_letter()+random_letter() for i in range(4)]
        self.stock_symbols = ["AAPL","QCOM","BRCM"]
        print self.stock_symbols
        self.last_quote = {}
        self.counter = 0
        self.time_format = "%a, %d %b %Y %H:%M:%S +0000"
#         self.qname = qname

    def get_quote(self):
        symbol = random.choice(self.stock_symbols)
        if symbol in self.last_quote:
            previous_quote = self.last_quote[symbol]
            new_quote = random.uniform(0.9*previous_quote, 1.1*previous_quote)
            if abs(new_quote) - 0 < 1.0:
                new_quote = 1.0
            self.last_quote[symbol] = new_quote
        else:
            new_quote = random.uniform(10.0, 250.0)
            self.last_quote[symbol] = new_quote
        self.counter += 1
        return (symbol, self.last_quote[symbol], time.gmtime(), self.counter)

    def monitor(self):
        while True:
            quote = self.get_quote()
            print("New quote is %s" % str(quote))
            self.publisher.publish(pickle.dumps((quote[0], quote[1], time.strftime(self.time_format, quote[2]), quote[3])), routing_key="")
            secs = random.uniform(0.1, 0.5)
            #print("Sleeping %s seconds..." % secs)
            time.sleep(secs)


def main():
    ticks=Ticker() 
    s = socket.socket()      
    port = 8091           
    s.bind(("localhost", port))        # Bind to the port
    print "Listening on port {p}...".format(p=port)
    s.listen(5)                 # Now wait for client connection. max q=5
    
    quote=[]
    while True:
        for i in range(100):
            quote.append(ticks.get_quote())
        print list(quote)
        try:
            
            client, addr = s.accept()
            ready = select.select([client,],[], [],2)  #wait for I/O complete
            if ready[0]:
                sym = client.recv(1024)
                print "received viwer's request is:" ,sym
                data=str(quote[len(quote)-1][1])
                client.send(data)
                print "send back to view is :",data
        except KeyboardInterrupt:
            print
            print "Stop."
            break
        except socket.error, msg:
            print "Socket error! %s" % msg
            break    


if __name__ == "__main__":
    main()

