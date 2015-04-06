//import JavaToJson;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.InetAddress;
import java.util.*;
import java.util.concurrent.*;
import java.lang.*;
import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.StringTokenizer;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.Helpers;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATBarHistoryType;
import at.shared.ATServerAPIDefines.ATConstituentListType;
import at.shared.ATServerAPIDefines.ATCursorType;
import at.shared.ATServerAPIDefines.ATGUID;
import at.shared.ATServerAPIDefines.ATQuoteFieldType;
import at.shared.ATServerAPIDefines.ATSYMBOL;
import at.shared.ATServerAPIDefines.ATStreamRequestType;
import at.shared.ATServerAPIDefines.ATSymbolType;
import at.shared.ATServerAPIDefines.SYSTEMTIME;
import at.utils.jlib.Errors;

//import org.json.*;
import org.json.simple.*;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;


public class StreamerRun 
{
	private static Socket socket;
	private ExecutorService exService;
	private final int POOL_SIZE = 10;
	private ServerSocket serverSocket;

	private static ActiveTickServerAPI serverapi;
	private static APISession apiSession;

	private	HashMap<String, ArrayList<String>> m_clientSymMap; 
	private HashMap<String, int> m_symRefMap; 
	private HashMap <String, SymData> m_symDataMap;
	private HashMap <String, DelayedTicks> m_symDelayMap;
	//private HashMap<String, ArrayList<String>> m_clientmap;
	//private ArrayList<String> m_allsymlist;
  	//private HashMap<String, SymData> m_map;

	//this is a time gap between Streamer's system clock and timestamp received in tick data. This value is set when first tick data is received and never changed. 
	private long m_atTimeGap=-1;


	
	//String host = "192.168.1.121";
	String m_hostIP = "localhost";
	int m_hostPort = 8091;

	String returnMessage;
	//	JavaToJson js = new JavaToJson();


		
	public StreamerRun() 
	{
	     	serverapi = new ActiveTickServerAPI();
		apiSession = new APISession(serverapi);

 		//init data structure
	 	m_clientSymMap = new HashMap<String, ArrayList<String>>();
		m_symRefMap = new HashMap<String, int>();
		m_symDataMap = new HashMap <String, SymData>();
		m_symDelayMap = new HashMap <String, DelayedTicks>();

//	 	m_allsymlist = new ArrayList<String>();
//	 	m_map = new HashMap<String, ArrayList<String[]>>() ;
   	}

   	public boolean Init() throws IOException, InterruptedException{

     	//initialize the api and login to the service
	      	serverapi.ATInitAPI();
		String atHostName = "activetick1.activetick.com";
	      	int atPort = 443;
	      	String guid = "80af4953bb7f4dcf85523ad332161eff";
	      	String userId = "liangcai";
	      	String password = "S@^@nt932456";
		ATGUID atguid = (new ATServerAPIDefines()).new ATGUID();
		atguid.SetGuid(guid);

		boolean rc = apiSession.Init(atguid, atHostName, atPort, userId, password, m_map);
		System.out.println("init status: " + (rc ? "ok" : "failed"));
		if (!rc)
	       		return false;
	      	Thread.sleep(5000);
	      	if(!apiSession.m_loginSucceed){
	        	System.out.println("Login failed!");
	         	return false;
	      	}

      //initialize the server socket
		InetAddress bindAdd = InetAddress.getByName(m_hostIP);
		serverSocket = new ServerSocket(m_hostPort, 100, bindAdd);
		int totalNum = Runtime.getRuntime().availableProcessors()*POOL_SIZE;
		exService = Executors.newFixedThreadPool(totalNum);		
		System.out.println("Server Started and listening to the port 8091");
      		return true;
	}


	public void acceptClient()
	{	
		while (true){
         		Socket socket = null;
			try{
	         		socket = serverSocket.accept();
		      		System.out.println("ready for next client");
	         		exService.execute(new Handler(socket, m_map));
			} 
		        catch (Exception e){
		      		e.printStackTrace();
		   	}	 		
      		}		
	}

   	class Handler implements Runnable{
   		private Socket socket;
   		private HashMap<String, ArrayList<String[]>> map;

   		public Handler(Socket socket,	HashMap<String, ArrayList<String[]>> map)		 {
   			this.socket = socket;
   			this.map = map;
   		}

	   	public void run() 
		{
        		ArrayList<String[]> lRet = new ArrayList<String[]>();
   			String[] rData = new String[5];
   		try{
   
   		   System.out.println("Socket accepted");
   			while(true){	
   			   InputStream is = socket.getInputStream();
   			   if (is.available() != 0 ){
   				   InputStreamReader isr = new InputStreamReader(is);
   				   BufferedReader br1 = new BufferedReader(isr);
   				   try{	
   					   String jstr = br1.readLine();
   					   System.out.println("Message received from client is "+jstr);
   					   if(jstr.length() > 0){
                        //is this part of the specification? Streamer is a server shared by multiple clients so it should not be shutdown by one client
   					       if(jstr.startsWith("quit"))
   							   break;
   						   String returnMessage =	"hi";
   						   JSONParser parser = new JSONParser();
   						   //Object oObj=JSONValue.parse(jstr);
   						   Object oObj;
   						   try{
   							   oObj = parser.parse(jstr);
   	   						   JSONObject obj = (JSONObject) oObj;
   	   						   JSONObject req	= (JSONObject)obj.get("request");
   	                           if (req==null){
   	                               System.out.println("receiving invalid request: " +jstr);
   	                               continue;
   	                            }
   	   						    String cmd = (String)req.get("command");
   	                            if (cmd.equalsIgnoreCase("subscribe"))
   	                            {
   	                            	JSONArray symlist = (JSONArray)req.get("symlist");
   	                            	String client = (String)req.get("client");
   	                            	processSubscribe(client, symlist);
   	                            }
   	                            else if (cmd.equalsIgnoreCase("unsubscribe"))
   	                            {
   	                            	String client = (String)req.get("client");
   	                            	processUnubscribe(client);   	                            	
   	                            }
   	                            else if(cmd.equalsIgnoreCase("update"))
   	                            {
   	                            	String client = (String)req.get("client");
   	                            	String interval = (String)req.get("interval");
   	                            	String mask = (String)req.get("mask");
   	                            	processMask(client, interval, mask);   	                            	
  	                            }
   						   }
   						   catch(ParseException pe){
                               System.out.println("received request is not a valid json input: " +jstr);
                               continue;
   						   }
                           catch(java.lang.ClassCastException e){
                               System.out.println("received json request contain invalid field type: " +jstr);
                               continue;
                           }
   						   
					   /*String cl = (String)req.get("client");
   						   String sbList = (String)req.get("symlist");
   						   String cmdStr;
   						   if (sbList.contains(",")){
   							   JSONArray sList = (JSONArray)req.get("symlist");
   							   Iterator<String> iterator = sList.iterator();
   							   cmdStr = iterator.next();
   							   while(iterator.hasNext()){	
   								   cmdStr =	"," + iterator.next();
   							   }
   						   }
   						   else{
   							   cmdStr = sbList;
   						   }
   						   cmd = cmd + " " + cmdStr;
   						   processInput(cmd);
                        */
   					   }
   				   }   
   				   catch (Exception e) {
   					   e.printStackTrace();
   					   System.out.println("IO error trying to read your input!");
   				   }
   			   }
   			}
   			apiSession.UnInit();
   			serverapi.ATShutdownAPI();
   		}
   		catch (Exception e) {
   			e.printStackTrace();
   		}
   		finally{
   			try{
   			   socket.close();
   			   System.out.println("Socket CLosed");
   			}
   			catch(Exception e){}
   		}
   	 }

   	/**************
   	 * //processSubscribe
   	 * @param client: client name
   	 * @param symlist: subscribed the symbol list for the client
   	 * @return response in json
   	 * First check each sym in the symlist has already been subscribed with the same client. 
   	 * Create a reduced symlist if necessary
   	 * subscribe with atapi. add all sym with success to the clientmap. For those failed, print the reason
   	 * return the whole list for the client
   	 */
   	public String processSubscribe(String client, List<String> symlist)
	{
   		ArrayList<String> reducedsymlist = new ArrayList<String>();
   		
		if(m_clientmap.get(client) == null){
			m_clientmap.put(client,  new ArrayList<String>());
		}
		ArrayList<String> exsymlist = m_clientmap.get(client);
		for (String sym : symlist) {
			if(!exsymlist.contains(sym))
				exsymlist.add(sym);
				reducedsymlist.add(sym);
			}
		}

		if(reducedsymlist.size()>0){
			//subscribe all sym in the reduced list.			
		}
		
		
		return "";
   		
    }

   	/***************
   	 * 
   	 * @param client: client name
   	 * @return response in json
   	 */
   	public String processUnsubscribe(String client)
    {
   		return "";
    }

   	/****************
   	 * 
   	 * @param client: client name
   	 * @param interval: must be one value in ["1s", "5s", "10s", "30s", "1m", "5m", "10m", "30m", "1h"]
   	 * @param mask: has to be 6 digits with 0 and 1
   	 * @return
   	 */
   	public String processUpdate(String client, String interval, String mask)
    {
   		return "";
    }
   	
   	
   	/**********************************************************************
   	 * //processInput
   	 * Notes:
   	 * -Process command line input
   	 * @throws IOException 
   	 **********************************************************************/

   
   	public void processInput(String userInput) throws IOException
   	{
   		StringTokenizer st = new StringTokenizer(userInput);
   		List ls = new ArrayList<String>();
   		while(st.hasMoreTokens())
   			ls.add(st.nextToken());
   		int count = ls.size();
   		
   		
   		
   		/**********************************************************************
   		 * //subscribeQuoteStream | unsubscribeQuoteStream
   		 * Example:
   		 * Single symbol request:
   		 * 		subscribeQuoteStream	AAPL
   		 * 		unsubscribeQuoteStream	AAPL
   		 * Multiple symbol request:
   		 * 		subscribeQuoteStream	AAPL,AMZN
   		 * 		unsubscribeQuoteStream	AAPL,AMZN
   		 **********************************************************************/
   		if(count >= 2 && ( ((String)ls.get(0)).equalsIgnoreCase("subscribeQuoteStream") ||
   				((String)ls.get(0)).equalsIgnoreCase("unsubscribeQuoteStream")))
   		//else if(cmd.equals("subscribe"))
   		{
   			String strSymbols = ls.get(1).toString();
   			//String strSymbols = "AAPL,AMZN";
   			List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
    
   			if(!strSymbols.isEmpty() && !strSymbols.contains(","))
   			{
   				ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbols);
   				lstSymbols.add(atSymbol);
   			}
   			else
   			{
   				StringTokenizer symbolTokenizer = new StringTokenizer(strSymbols, ",");
   				while(symbolTokenizer.hasMoreTokens())
   				{
   					ATSYMBOL atSymbol = Helpers.StringToSymbol(symbolTokenizer.nextToken());
   					lstSymbols.add(atSymbol);
   				}
   			}			
   			
   			ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
   			requestType.m_streamRequestType = ((String)ls.get(0)).equalsIgnoreCase("subscribeQuoteStream") ? 
   											ATStreamRequestType.StreamRequestSubscribe : ATStreamRequestType.StreamRequestUnsubscribe;
   			//requestType.m_streamRequestType = ATStreamRequestType.StreamRequestSubscribe;
   			long request = apiSession.GetRequestor().SendATQuoteStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
   			
   			System.out.println("SEND444 " + request + ": " + ls.get(0).toString() + " request [" + strSymbols + "]");
   			if(request < 0)
   			{
   				System.out.println("Error = " + Errors.GetStringFromError((int)request));
   			}else{
   				returnMessage = "Subscribed!!";
   			}
   			
   			
   			OutputStream os = socket.getOutputStream();
   			OutputStreamWriter osw = new OutputStreamWriter(os);
   			//PrintWriter pw = new PrintWriter(os);
   	BufferedWriter bw = new BufferedWriter(osw);
   	//System.out.println(returnMessage);
   			try {
   				bw.write(returnMessage);
   			} catch (IOException e) {
   				// TODO Auto-generated catch block
   				e.printStackTrace();
   			}
   	//pw.println(returnMessage);
   			System.out.println("Message sent to the client is "+returnMessage);
   			
   			bw.flush();
   		}
   		
   		/**********************************************************************
   		 * //subscribeQuotesOnlyQuoteStream | unsubscribeQuotesOnlyQuoteStream
   		 * Example:
   		 * Single symbol request:
   		 * 		StreamRequestSubscribeQuotesOnly	AAPL
   		 * 		StreamRequestUnsubscribeQuotesOnly	AAPL
   		 * Multiple symbol request:
   		 * 		StreamRequestSubscribeQuotesOnly	AAPL,AMZN
   		 * 		StreamRequestUnsubscribeQuotesOnly	AAPL,AMZN
   		 **********************************************************************/
   		else if(count >= 2 && ( ((String)ls.get(0)).equalsIgnoreCase("subscribeQuotesOnlyQuoteStream") ||
   				((String)ls.get(0)).equalsIgnoreCase("unsubscribeQuotesOnlyQuoteStream")))
   		{
   			String strSymbols = ls.get(1).toString();
   			List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
   
   			if(!strSymbols.isEmpty() && !strSymbols.contains(","))
   			{
   				ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbols);
   				lstSymbols.add(atSymbol);
   			}
   			else
   			{
   				StringTokenizer symbolTokenizer = new StringTokenizer(strSymbols, ",");
   				while(symbolTokenizer.hasMoreTokens())
   				{
   					ATSYMBOL atSymbol = Helpers.StringToSymbol(symbolTokenizer.nextToken());
   					lstSymbols.add(atSymbol);
   				}
   			}			
   			
   			ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
   			requestType.m_streamRequestType = ((String)ls.get(0)).equalsIgnoreCase("subscribeQuotesOnlyQuoteStream") ? 
   											ATStreamRequestType.StreamRequestSubscribeQuotesOnly : ATStreamRequestType.StreamRequestUnsubscribeQuotesOnly;
   			
   			long request = apiSession.GetRequestor().SendATQuoteStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
   			
   			System.out.println("SENDeeeeee " + request + ": " + ls.get(0).toString() + " request [" + strSymbols + "]");
   			if(request < 0)
   			{
   				System.out.println("Error = " + Errors.GetStringFromError((int)request));
   			}
   		}else if (count == 1	&& ( ((String)ls.get(0)).equalsIgnoreCase("update"))){
   			String strSymbols = "AAPL";
   			System.out.println("get map!!");
   			HashMap<String, ArrayList<String[]>> map = apiSession.GetStreamer().getMap();
   			if (map.isEmpty()){
   				System.out.println("Map is empty!!!");
   			}else{
   				ArrayList<String[]> ret = map.get(strSymbols);
   				System.out.println("S size is " + ret.size());
   				for(String[] s : ret){
   					System.out.println("[" + s[0] + ", " + s[1] + ", " + s[2]+ ", "+ s[3] + ", " +s[4] + "]");
   					
   					OutputStream os = socket.getOutputStream();
   				OutputStreamWriter osw = new OutputStreamWriter(os);
   				//PrintWriter pw = new PrintWriter(os);
   			BufferedWriter bw = new BufferedWriter(osw);
   			//System.out.println(returnMessage);
   				bw.write(returnMessage);
   			//pw.println(returnMessage);
   				System.out.println("Message sent to the client is "+returnMessage);
   				
   				bw.flush();
   				}
   			}
   		}
   		/**********************************************************************
   		 * //subscribeTradesOnlyQuoteStream | unsubscribeTradesOnlyQuoteStream
   		 * Example:
   		 * Single symbol request:
   		 * 		subscribeTradesOnlyQuoteStream	AAPL
   		 * 		unsubscribeTradesOnlyQuoteStream	AAPL
   		 * Multiple symbol request:
   		 * 		subscribeTradesOnlyQuoteStream	AAPL,AMZN
   		 * 		unsubscribeTradesOnlyQuoteStream	AAPL,AMZN
   		 **********************************************************************/
   		else if(count >= 2 && ( ((String)ls.get(0)).equalsIgnoreCase("subscribeTradesOnlyQuoteStream") ||
   				((String)ls.get(0)).equalsIgnoreCase("unsubscribeTradesOnlyQuoteStream")))
   		{
   			String strSymbols = ls.get(1).toString();
   			List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
   
   			if(!strSymbols.isEmpty() && !strSymbols.contains(","))
   			{
   				ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbols);
   				lstSymbols.add(atSymbol);
   			}
   			else
   			{
   				StringTokenizer symbolTokenizer = new StringTokenizer(strSymbols, ",");
   				while(symbolTokenizer.hasMoreTokens())
   				{
   					ATSYMBOL atSymbol = Helpers.StringToSymbol(symbolTokenizer.nextToken());
   					lstSymbols.add(atSymbol);
   				}
   			}			
   			
   			//ATStreamRequestType.
   			
   			ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
   			requestType.m_streamRequestType = ((String)ls.get(0)).equalsIgnoreCase("subscribeTradesOnlyQuoteStream") ? 
   											ATStreamRequestType.StreamRequestSubscribeTradesOnly : ATStreamRequestType.StreamRequestUnsubscribeTradesOnly;
   			
   			long request = apiSession.GetRequestor().SendATQuoteStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
   			
   			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbols + "]");
   			if(request < 0)
   			{
   				System.out.println("Error = " + Errors.GetStringFromError((int)request));
   			}
   		}
   		
   		/**********************************************************************
   		 * //MarketHolidays
   		 * Example:
   		 * Notes:
   		 * 	-Currently not being used
   		 **********************************************************************/
   		else if(count >= 2 && ( ((String)ls.get(0)).equalsIgnoreCase("getMarketHolidays")))
   		{
   			short yearsGoingBack = Short.parseShort(ls.get(1).toString());
   			short yearsGoingForward = Short.parseShort(ls.get(2).toString());
   			
   			long request = apiSession.GetRequestor().SendATMarketHolidaysRequest(yearsGoingBack, yearsGoingForward, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
   
   			System.out.println("SEND " + request + ":MarketHolidays request for " + yearsGoingBack + " years back and " + yearsGoingForward + " years forward");
   			if(request < 0)
   			{
   				System.out.println("Error = " + Errors.GetStringFromError((int)request));
   			}
   		}			
   	}
   
   	
   }

   public static void main(String[] args) throws IOException, InterruptedException 
   {		
      StreamerRun sr = new StreamerRun();
      if (sr.Init())
         sr.acceptClient();
      else{
    	  System.out.println("Fail to initialize Streamer. Exiting");
    	  System.exit(-1);
      }
    	  
   }
}
		 
