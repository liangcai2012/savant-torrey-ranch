from jpype import *
#from at.feedapi import *
#from at.shared import * 
#from at.utils.jlib import *
#from atapi.wrapper import *
from datetime import *
from atutil import *
import os, sys

#define a set of global variables
g_atclass = None
g_atapi = None
g_atapisession = None
g_atapirequestor = None
g_atapidefined = None


#from atpyapi_jpype import *

#Function: display stock charts of a certain symbol for a time period (smaller than one day). 
# The charts contain three chart: 
#    1) close price of each time unit 
#    2) price range in each time unit
#    3) volumn in each time unit
# Usage: atshow SYM DATE [TIMEDURATION] [TIMEUNIT]
#
# TIMEDURATION takes the form of STARTTIME[-ENDTIME|+DURATION]. Default value is 4-18
# STARTTIME and ENDTIME are numbers. If it is less than 100, then it is hour. elif it is less than 10000, the number is hhmm, otherwise it is hhmmss
# DURATION must be like 3h, 15m, 30m etc.  
# eg:  9-12 means 9:00-12:00,  930-12 means 9:30-12:00, 1030+2h means 10:30-12:30
#
# TIMEUNIT must be either m or s, by default, it is m if the range exceeds 2 hour

# the application will keep taking input of new timeduration


#input: symbol, year, month, day range


class ATBase:
    def afterLogin(self, resp):
        raise NotImplementedError

    def afterHistoryTickReceived(self, resp, ticks):
        raise NotImplementedError
        
    def setGlobal(self, api, apisession, requestor, defined, helper):
	self.m_api = api
	self.m_apisession = apisession
	self.m_requestor = requestor 
	self.m_defined = defined
	self.m_helper = helper 



class RealCallback:
	def onLoginResponse(self, req, resp):
                global g_atclass
                global g_atapidefined

		strResp = "" 
		#loginRespType = self.m_defined.ATLoginResponseType(self.m_defined)
                LRT = JClass('at.shared.ATServerAPIDefines$ATLoginResponseType')
		loginRespType = LRT(g_atapidefined)	
		if resp == loginRespType.LoginResponseSuccess:
		    strResp = "Success"
		elif resp == loginRespType.LoginResponseInvalidUserid:
		    strResp = "InvalidUserid"
		elif resp == loginRespType.LoginResponseInvalidPassword:
		    strResp = "InvalidPassword"
		else:
		    strResp = "unknown"
		    
		print "RECV " + str(req) + ": Login Response ["+strResp+"]"

		#self.m_atclass.afterLogin(resp)
		g_atclass.afterLogin(resp)

		#symlist = []
		#symlist.append(helper.StringToSymbol("QCOM"))
		#sreqtype = defined.ATStreamRequestType(defined)
		#sreqtype.m_streamRequestType = sreqtype.StreamRequestSubscribeTradesOnly
		#request = requestor.SendATQuoteStreamRequest(symlist, sreqtype, api.DEFAULT_REQUEST_TIMEOUT)
		
		#if request < 0:
		#	print("Fail to send stream request, error = " + Errors.GetStringFromError(request));
		#else:
		#	print 'send stream request:', request



	def onStatusChange(self, sctype):
                global g_atapidefined
                global g_atapi
                global g_atapisession
		strResp = "" 
		#statusType = self.m_defined.ATSessionStatusType(self.m_defined)	
                ATSST = JClass('at.shared.ATServerAPIDefines$ATSessionStatusType')
		statusType = ATSST(g_atapidefined)	
		if sctype == statusType.SessionStatusConnected:
			strResp = "Connected"
		elif sctype== statusType.SessionStatusDisconnected:
			strResp = "Disconnected"
		elif sctype == statusType.SessionStatusDisconnectedDuplicateLogin:
			strResp = "DisconnectedDuplicateLogin"
		else:
			strResp = "UnknownStatusChange"

		print "RECV " + ": status change["+strResp+"]"
		if sctype == statusType.SessionStatusConnected:
			#lastreq = self.m_api.ATCreateLoginRequest(self.m_apisession.GetSession(), "liangcai", "S@^@nt932456", self.m_apisession)
			#self.m_api.ATSendRequest(self.m_apisession.GetSession(), lastreq, self.m_api.DEFAULT_REQUEST_TIMEOUT, self.m_apisession)
			lastreq = g_atapi.ATCreateLoginRequest(g_atapisession.GetSession(), "liangcai", "S@^@nt932456", g_atapisession)
			g_atapi.ATSendRequest(g_atapisession.GetSession(), lastreq, g_atapi.DEFAULT_REQUEST_TIMEOUT, g_atapisession)
			#print "SEND (", lastreq, "): Login request"


class ReqCallback:
	#def setATClass(self, c):
	#	self.m_atclass = c

	def onTickHistoryDbReady(self, reqid, resp, ticks):
            global g_atclass
	    #self.m_atclass.afterHistoryTickReceived(resp, ticks)
	    g_atclass.afterHistoryTickReceived(resp, ticks)
		
	def onBarHistoryDbReady(self, reqid, resp, bars):
            #global g_atclass
	    #self.m_atclass.afterHistoryBarReceived(resp, bars)
	    g_atclass.afterHistoryBarReceived(resp, bars)



class ATShow(ATBase):
	def __init__(self, symbol, date, span, tu):

		#these are const globally
		self.m_symbolstr = symbol 
                self.m_symbol = None
		self.m_span = span
		self.m_date = date

		self.MAXSTEP = 600
		self.MINSTEP = 60 
		self.BEGINSTEP = 240

                self.m_start = date*1000000 + span[0]
                self.m_end = date*1000000 + span[1]

                self.m_pstart = self.m_start 
                self.m_pend = self.m_start 
		self.m_step = self.BEGINSTEP 

		self.m_opened = False
		self.m_closed = False
		self.m_high_sofar = 0
		self.m_low_sofar = 1000000

		self.m_count = 0
		self.m_prehournum= 0
		self.m_afterhourindex= 0
		self.m_volume = 0

	def afterLogin(self, resp):
		self.m_starttime = datetime.now()
		self.dldata()



	def dldata(self):
		print self.m_symbolstr, self.m_pend, self.m_end, self.m_step
                Helpers = JClass("at.feedapi.Helpers")
                if self.m_symbol == None:
                        self.m_symbol = Helpers.StringToSymbol(self.m_symbolstr)
		if self.m_pend >= self.m_end:
			return
		else:
			self.m_pstart = self.m_pend
			self.m_pend = timeadd(self.m_pstart, self.m_step)
			if self.m_pend > self.m_end:
				self.m_pend = self.m_end
			self.begintime = Helpers.StringToATTime(str(self.m_pstart));
			self.endtime = Helpers.StringToATTime(str(self.m_pend)); 
                        
			request= self.m_requestor.SendATTickHistoryDbRequest(self.m_symbol, True, True, self.begintime, self.endtime, self.m_api.DEFAULT_REQUEST_TIMEOUT);
			if request < 0:
				print("Fail to send tick history request. Error = " + Errors.GetStringFromError(request));
				exit(-1) 
		return 


	def afterHistoryTickReceived(self, resp, ticks):
                AHRT = JClass("at.shared.ATServerAPIDefines$ATTickHistoryRecordType")
                ATCT = JClass("at.shared.ATServerAPIDefines$ATTradeConditionType")
		print self.m_pstart, self.m_step, len(ticks) 

		if len(ticks) == 20000:
			#maximum reached, the step must be smaller and resend the same request
			if self.m_step == self.MINSTEP:
				print "unexpected large number of ticks within the smallest step"
				exit(-1)
			self.m_step = self.MINSTEP 
			self.dldata()
			return
			
		#self.m_count += len(ticks) 

		#adjust the step 
		if len(ticks) < 5000:
			if self.m_step < self.MAXSTEP:
				self.m_step *= 2

		skipvolume = False
		for tick in ticks:
			if tick.recordType.m_historyRecordType == AHRT.TickHistoryRecordTrade:
				for i in range(4):
					if not self.m_opened and tick.lastCondition[i].m_atTradeConditionType == ATCT.MarketCenterOfficialOpen:
						skipvolume = True
						#self.m_tick_res[0] = tick.lastPrice.price
						self.m_opened = True
						self.m_prehournum = self.m_count
						break	#volume in this tick should be skipped
					if not self.m_closed and tick.lastCondition[i].m_atTradeConditionType == ATCT.MarketCenterOfficialClose:
						skipvolume = True
						#self.m_tick_res[1] = tick.lastPrice.price
						self.m_closed = True
						self.m_afterhourindex = self.m_count
					break

				if not skipvolume:
					self.m_volume += tick.lastSize
				skipvolume = False

				self.m_count +=1
				#if self.m_opened and not self.m_closed: 
				#	if tick.lastPrice.price > self.m_high_sofar:
				#		self.m_high_sofar = tick.lastPrice.price
				#	if tick.lastPrice.price < self.m_low_sofar:
				#		self.m_low_sofar = tick.lastPrice.price

				#print str(tick.lastDateTime.year)+str(tick.lastDateTime.month)+str(tick.lastDateTime.day)+str(tick.lastDateTime.hour)+str(tick.lastDateTime.minute)+str(tick.lastDateTime.second)+str(tick.lastDateTime.milliseconds), 'TRADE\tlast:', tick.lastPrice.price, '\tlastsize:', tick.lastSize, '\tlastexch:', tick.lastExchange.m_atExchangeType, '\tcond:', tick.lastCondition[0].m_atTradeConditionType, tick.lastCondition[1].m_atTradeConditionType, tick.lastCondition[2].m_atTradeConditionType, tick.lastCondition[3].m_atTradeConditionType
				recordstr = str(attime2int(tick.lastDateTime, isdate = False))+',\t' +\
								str(tick.lastPrice.price) + ',\t' + str(tick.lastSize) + ',\t' +\
								str(tick.lastExchange.m_atExchangeType) + ',\t' +\
								str(tick.lastCondition[0].m_atTradeConditionType) +' ' +\
								str(tick.lastCondition[1].m_atTradeConditionType) +' ' +\
								str(tick.lastCondition[2].m_atTradeConditionType) +' ' +\
								str(tick.lastCondition[3].m_atTradeConditionType) + '\n'
				#self.m_fsymday.write(recordstr)
				print recordstr

		#self.dldata()
		return


def quit_usage():
    print "Invalid argument"
    print "Usage: atshow SYM DATE [TIMEDURATION] [TIMEUNIT]" 
    exit(-1)

def main():

    global g_atclass
    global g_atapi
    global g_atapisession
    global g_atapirequestor
    global g_atapidefined
#parse args
    if len(sys.argv) < 3:
        quit_usage()
    symb = sys.argv[1]

    try:
        date = int(sys.argv[2])
    except ValueError:
        quit_usage()
    
    if date/10000 > 2014 or date/10000 < 2006:
        quit_usage()
    if (date/100)%100 > 12:
        quit_usage()
    if (date)%100 > 31:
        quit_usage()
    
    start= 40000   #default is the pre-market open hour
    end= 180000     #default is the after-market close hour
    
    if len(sys.argv) ==4:
        if '-' in sys.argv[3]:
    	    p=sys.arg[2].split('-')
    	    start=timenorm(p[0])
            if start < 0:
                quit_usage()
    	    end=timenorm(p[1])
            if end < 0:
                quit_usage()
    
        elif '+' in sys.argv[3]:
    	    p=sys.arg[2].split('+')
    	    start=timenorm(p[0])
            if start < 0:
                quit_usage()
            dur = tdurmorm(p[1]) 
            if dur < 0:
                quit_usage()
    	    end = timeadd(start, dur)
            if end < 0:
                quit_usage()
    
        else:
    	    start = timenorm(sys.argv[3])
    
    print 'start =', start
    #if not specified, the time unit is minute if duration bigger than 2 hours, or second otherwise
    tuminute = 's'    
    if end - start > 20000:
        tuminute = True
    
    if len(sys.argv) == 5:
        if sys.argv[4] == 's':
    	    tuminute= False
        elif sys.argv[4] == 'm':
    	    tuminute = True
        else:
    	    print "invalid time unit. quiting"
    	    exit(-1)
    
# Set up API env
    startJVM(getDefaultJVMPath())
    
    atshared = JPackage('at').shared
    atfeedapi = JPackage('at').feedapi
    wrapper = JPackage('atapi').wrapper
    
    #CB = atshared.ATCallback
    
    Defined = atshared.ATServerAPIDefines
    g_atapidefined = Defined()

    Helpers = atfeedapi.Helpers
    g_atapihelper = Helpers()
    
    Guid = JClass('at.shared.ATServerAPIDefines$ATGUID')
    guid = Guid(g_atapidefined) 
    guid.SetGuid("80af4953bb7f4dcf85523ad332161eff")
    print guid
    
    
    ST = JClass('at.shared.ATServerAPIDefines$ATSessionStatusType')
    st = ST(g_atapidefined)
    
    #m_atclass = c
    
    #streamtype = defined.ATStreamRequestType(defined)
    #streamtype.m_streamRequestType = streamtype.StreamRequestSubscribe
    
    realcallback = RealCallback()
    reqcallback = ReqCallback()
    APICB = wrapper.APICallback
    APIRCB = wrapper.APIReqCallback
    #cb = JProxy('atapi.wrapper.APICallback', inst=realcallback)
    cb = JProxy(APICB, inst=realcallback)
    #rcb = JProxy('atapi.wrapper.APIReqCallback', inst=ReqCallback())
    rcb = JProxy(APIRCB, inst=reqcallback)

    g_atclass = ATShow(symb, date, [start, end], tuminute)
    #cb.setATClass(atclass)
    #rcb.setATClass(atclass)
    
    API = atfeedapi.ActiveTickServerAPI
    g_atapi = API()
    g_atapi.ATInitAPI()
    
    
    #APISession = wrapper.APISession
    APISession = JClass('atapi.wrapper.APISession')
    g_atapisession = APISession(g_atapi, cb, rcb)
    
    g_atapisession.Init(guid, "activetick1.activetick.com", 443, "", "")
    #lastreq = g_atapi.ATCreateLoginRequest(g_atapisession.GetSession(), "liangcai", "S@^@nt932456", g_atapisession)
    #print 'lastreq', lastreq
    #print g_atapi.DEFAULT_REQUEST_TIMEOUT
    #print g_atapisession.GetSession()
    #g_atapi.ATSendRequest(g_atapisession.GetSession(), 1, g_atapi.DEFAULT_REQUEST_TIMEOUT, g_atapisession)


    g_atapirequestor = g_atapisession.GetRequestor()
    
    g_atclass.setGlobal(g_atapi, g_atapisession, g_atapirequestor, g_atapidefined, g_atapihelper)

    raw_input("Press Enter to continue...")
    #cb.setGlobal(api, apisession, defined)
    #cb.onStatusChange(0)
	

if __name__ == "__main__":
	main()
