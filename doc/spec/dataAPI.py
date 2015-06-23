class DataError(RuntimeError):
   def __init__(self, args):
      self.args = args

class DataAPI():

    #cound is a static variable and used to generate a unique name for each Data instance to access streamer. 
    #the unique name shall be clientName+'_'+str(count), where clientName is specified in __init__ method. 	
    count=0



    # initialiazation for getting real time or historical data interface.
	# if no serverIPaddress or port is specified then this inteface instance 
    #is for history data. Otherwise it is for streaming data

    # generates a DataError exception if it fails to connect to the streamer server.
    def __init__(self, clientName, serverIP= None, port= None):
        raise NotImplementedError("Subclass must implement abstract method")

	# subscribe a list of symbals in this interface instance for obtaining realtime.
    # raise an error if serverIp or port is not specified in __init__ 
	def subscribeRealtime(self, symList):

    # subscrib a list of tuples [{sym, time}] in this instance for obtaining history.
    # time format: YYYYMMDD-HHMMSS
    # raise an error if serverIp and port are specified in __init__
    # read multiple history data in one instance is not common. In most case the list 
    # should contain only one sym-time tuple. 
	def subscribeHistory(self, symPeriodList):


	# unsubscribe part of symbols previous subscribed 
	def unsubscribeRealtime(self, symList):

    # unsubscribe part of the symbol-time tuples previous subscribed. For history data, this api has no real effect
	def unsubscribeHistory(self, symPeriodList):

	# update data with given interval
    # return a list of data for all subscribed symbol or symbol-time tuples. The returned data format can be seen in 
    def update(self, interval, bar_mask, ma_mask):
        raise NotImplementedError("Subclass must implement abstract method")

#    def setReponseMsg(self, client, symbol, bar, ma, delay, timestamp, interval):
#        data = {"symbol": symbol,\
#                "bar": bar, \
#                "ma": ma,\
#                  "delay" :delay}
#        msg = {"client": client, "timestamp": timestamp ,\
#               "interval": interval,
#               "data":data
#               }
#        return msg

