package atapi.wrapper;

//package Streamer;

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


public class StreamerRun 
{
    private static Socket socket;
    private ExecutorService exService;
    private final int POOL_SIZE = 10;
	private HashMap<String, ArrayList<String[]>> map;
    private ServerSocket serverSocket;

    
    public static ActiveTickServerAPI serverapi;
	public static APISession apiSession;
	
	
    //String host = "192.168.1.121";
    String host = "localhost";
    int port = 8091;
    int i = 0;    
    int totalNum = 0;
	
int count = 0;    

	String returnMessage;
 //   JavaToJson js = new JavaToJson();

    public static void main(String[] args) throws IOException 
    {       HashMap<String, ArrayList<String[]>> map = new HashMap<String, ArrayList<String[]>>() ;
            new StreamerRun(map).acceptClient();
    }
         
    public StreamerRun(HashMap<String, ArrayList<String[]>> map) throws IOException{
		    
    	
    	
            InetAddress bindAdd = InetAddress.getByName(host);
            
            serverSocket = new ServerSocket(port, 100, bindAdd);
            
            totalNum = Runtime.getRuntime().availableProcessors()*POOL_SIZE;
        
            exService = Executors.newFixedThreadPool(totalNum);        
       
            this.map = map;

            System.out.println("Server Started and listening to the port 8091");
    }

    public void acceptClient()
    {    
        while (true){
            Socket socket = null;
            try{
                socket = serverSocket.accept();
                System.out.println("ready for next client");
                
                exService.execute(new Handler(socket, map));
            
            } catch (Exception e){
                e.printStackTrace();
            } 		
        }       
    }

class Handler implements Runnable{
	
	private Socket socket;
	private HashMap<String, ArrayList<String[]>> map;
	
	public Handler(Socket socket,  HashMap<String, ArrayList<String[]>> map){
		this.socket = socket;
		this.map = map;
	
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
		
		

		//init
		 if(count >= 5 && ((String)ls.get(0)).equalsIgnoreCase("init"))
		{
			String serverHostname = ls.get(1).toString();
			int serverPort = new Integer(ls.get(2).toString());
			String apiKey = ls.get(3).toString();
			String userId = ls.get(4).toString();
			String password = ls.get(5).toString();
			HashMap<String, ArrayList<String[]>> map = new HashMap<String, ArrayList<String[]>>();
			if(apiKey.length() != 32)
			{
				//InvalidGuidMessage();
				return;
			}
			
			ATGUID atguid = (new ATServerAPIDefines()).new ATGUID();
			atguid.SetGuid(apiKey);
			
			boolean rc = apiSession.Init(atguid, serverHostname, serverPort, userId, password, map);
			System.out.println("\ninit status: " + (rc == true ? "ok" : "failed"));
		}

		/**********************************************************************
		 * //getQuoteDb  
		 * Examples:
		 * 		getQuoteDb AAPL
		 * 		getQuoteDb AAPL,AMZN
		 * 		getQuoteDb AAPL,ADBE,AMZN,ACLS,AKAM,ASTM,AAWW,ABMD,ACAT
		 **********************************************************************/
		else if(count >= 2 && ((String)ls.get(0)).equalsIgnoreCase("getQuoteDb"))
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
			List<ATQuoteFieldType> lstFieldTypes = new ArrayList<ATQuoteFieldType>();
			ATServerAPIDefines atServerAPIDefines = new ATServerAPIDefines();
			lstFieldTypes.add(atServerAPIDefines.new ATQuoteFieldType(ATQuoteFieldType.LastPrice));
			lstFieldTypes.add(atServerAPIDefines.new ATQuoteFieldType(ATQuoteFieldType.Volume));
			lstFieldTypes.add(atServerAPIDefines.new ATQuoteFieldType(ATQuoteFieldType.LastTradeDateTime));
			lstFieldTypes.add(atServerAPIDefines.new ATQuoteFieldType(ATQuoteFieldType.ProfileShortName));

			long request = apiSession.GetRequestor().SendATQuoteDbRequest(lstSymbols, lstFieldTypes, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);

			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbols + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}
		/**********************************************************************
		 * //getOptionChain
		 * Examples:
		 * 		getOptionChain AAPL
		 **********************************************************************/
		else if(count == 2 && ((String)ls.get(0)).equalsIgnoreCase("getOptionChain"))
		{
			String strSymbol = ls.get(1).toString();
			ATConstituentListType constituentType = (new ATServerAPIDefines()).new ATConstituentListType(ATConstituentListType.ConstituentListOptionChain);
			
			long request = apiSession.GetRequestor().SendATConstituentListRequest(constituentType, strSymbol.getBytes(), ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);  

			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}

		}
		
		/**********************************************************************
		 * 1 - REGULAR
		 * //getIntradayHistoryBars
		 * Examples:
		 * 		getIntradayHistoryBars CSCO 1 20100924130000 20100924130500
		 * 		getDailyHistoryBars CSCO 20100801100000 20100924130500
		 * 		getWeeklyHistoryBars CSCO 20100801100000 20100924130500
		 **********************************************************************/
		else if(count >= 5 && ((String)ls.get(0)).equalsIgnoreCase("getIntradayHistoryBars"))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			short minutes = Short.parseShort(ls.get(2).toString());
			
			SYSTEMTIME beginDateTime = Helpers.StringToATTime(ls.get(3).toString());
			SYSTEMTIME endDateTime = Helpers.StringToATTime(ls.get(4).toString());
			
			ATBarHistoryType barHistoryType = (new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryIntraday);
			long request = apiSession.GetRequestor().SendATBarHistoryDbRequest(atSymbol, barHistoryType,
					minutes, beginDateTime, endDateTime, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);

			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}	
		
		/**********************************************************************
		 * 3
		 * //getIntradayHistoryBars
		 * Examples:
		 * 		getIntradayHistoryBars CSCO 1 20100924130000 20100924130500
		 * 		getDailyHistoryBars CSCO 20100801100000 20100924130500
		 * 		getWeeklyHistoryBars CSCO 20100801100000 20100924130500
		 **********************************************************************/
		else if(count == 6 && ((String)ls.get(0)).equalsIgnoreCase("getIntradayHistoryBars"))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			short minutes = Short.parseShort(ls.get(2).toString());
			
			SYSTEMTIME beginDateTime = Helpers.StringToATTime(ls.get(3).toString());
			int numRecords = Integer.parseInt(ls.get(4).toString());
			byte byteCursorType = (byte)Integer.parseInt(ls.get(5).toString());
			
			ATBarHistoryType barHistoryType = (new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryIntraday);
			long request = apiSession.GetRequestor().SendATBarHistoryDbRequest(atSymbol, barHistoryType, minutes, beginDateTime, numRecords, 
					(new ATServerAPIDefines()).new  ATCursorType(byteCursorType), ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);

			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}	

		
		
		/**********************************************************************
		 * //1 - REGULAR 
		 * //getDailyHistoryBars | getWeeklyHistoryBars
		 * Example:
		 * 		getDailyHistoryBars CSCO 20100801100000 20100924130500
		 **********************************************************************/
		else if(count == 4 && ( ((String)ls.get(0)).equalsIgnoreCase("getDailyHistoryBars") ||
								((String)ls.get(0)).equalsIgnoreCase("getWeeklyHistoryBars")))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			
			SYSTEMTIME beginDateTime = Helpers.StringToATTime(ls.get(2).toString());
			SYSTEMTIME endDateTime = Helpers.StringToATTime(ls.get(3).toString());
			ATBarHistoryType barHistoryType = (((String)ls.get(0)).equalsIgnoreCase("getDailyHistoryBars")) ? (new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryDaily) :
				(new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryWeekly);
										
			long request = apiSession.GetRequestor().SendATBarHistoryDbRequest(atSymbol, barHistoryType, 
					(short)0, beginDateTime, endDateTime, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);

			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}		

		/**********************************************************************
		 * //2 - 
		 * //getDailyHistoryBars | getWeeklyHistoryBars
		 * Example:
		 * 		getDailyHistoryBars CSCO 5
		 **********************************************************************/
		else if(count == 3 && ( ((String)ls.get(0)).equalsIgnoreCase("getDailyHistoryBars") ||
								((String)ls.get(0)).equalsIgnoreCase("getWeeklyHistoryBars")))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			int numRecords = Integer.parseInt(ls.get(2).toString());
			ATBarHistoryType barHistoryType = (((String)ls.get(0)).equalsIgnoreCase("getDailyHistoryBars")) ? (new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryDaily) :
				(new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryWeekly);
										
			long request = apiSession.GetRequestor().SendATBarHistoryDbRequest(atSymbol, barHistoryType, (short)0, 
					numRecords, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);

			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}		

		/**********************************************************************
		 * //3 - 
		 * //getDailyHistoryBars | getWeeklyHistoryBars
		 * Example:
		 * 		getDailyHistoryBars CSCO 20100601100000 500 1
		 **********************************************************************/
		else if(count == 5 && ( ((String)ls.get(0)).equalsIgnoreCase("getDailyHistoryBars") ||
								((String)ls.get(0)).equalsIgnoreCase("getWeeklyHistoryBars")))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			SYSTEMTIME beginDateTime = Helpers.StringToATTime(ls.get(2).toString());
			int numRecords = Integer.parseInt(ls.get(3).toString());
			byte byteCursorType = (byte)Integer.parseInt(ls.get(4).toString());
			ATBarHistoryType barHistoryType = (((String)ls.get(0)).equalsIgnoreCase("getDailyHistoryBars")) ? (new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryDaily) :
				(new ATServerAPIDefines()).new ATBarHistoryType(ATBarHistoryType.BarHistoryWeekly);
										
			long request = apiSession.GetRequestor().SendATBarHistoryDbRequest(atSymbol, barHistoryType, (short)0, beginDateTime, numRecords, 
					(new ATServerAPIDefines()).new  ATCursorType(byteCursorType), ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			
			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}		
		
		/**********************************************************************
		 * 1 - REGULAR
		 * //Ticks
		 * Example:
		 * 		getTicks CSCO 20100924131112 20100924134012
		 **********************************************************************/
		else if(count == 4 && ((String)ls.get(0)).equalsIgnoreCase("getTicks"))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			
			SYSTEMTIME beginDateTime = Helpers.StringToATTime(ls.get(2).toString());
			SYSTEMTIME endDateTime = Helpers.StringToATTime(ls.get(3).toString());
									
			long request = apiSession.GetRequestor().SendATTickHistoryDbRequest(atSymbol, true, true, beginDateTime, endDateTime, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			
			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}

		/**********************************************************************
		 * 2 - 
		 * //Ticks
		 * Example: 
		 * 		getTicks CSCO 100
		 **********************************************************************/
		else if(count == 3 && ((String)ls.get(0)).equalsIgnoreCase("getTicks"))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			
			int numRecords = Integer.parseInt(ls.get(2).toString());
									
			long request = apiSession.GetRequestor().SendATTickHistoryDbRequest(atSymbol, true, true, numRecords, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			
			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}


		/**********************************************************************
		 * 3 - 
		 * //Ticks
		 * Example:100 records going foward from given time
		 * 		getTicks CSCO 20100924131112 100 1
		 **********************************************************************/
		else if(count == 5 && ((String)ls.get(0)).equalsIgnoreCase("getTicks"))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			
			SYSTEMTIME beginDateTime = Helpers.StringToATTime(ls.get(2).toString());
			int numRecords = Integer.parseInt(ls.get(3).toString());
			byte byteCursorType = (byte)Integer.parseInt(ls.get(4).toString());
									
			long request = apiSession.GetRequestor().SendATTickHistoryDbRequest(atSymbol, true, true, beginDateTime, numRecords, 
					(new ATServerAPIDefines()).new  ATCursorType(byteCursorType), ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			
			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}

		
		
		/**********************************************************************
		 * //MarketMovers
		 * Symbols: NG - NetGainers, NL - NetLoosers, PG - PercentGainers, PL - PercentLoosers, VL - Volume
		 * Exchange: A - Amex, U - OTCBB, N - NyseEuronext, Q - NasdaqOmx
		 * 
		 * Example:
		 * 		getMarketMovers NG Q
		 **********************************************************************/
		else if(count >= 3 && ((String)ls.get(0)).equalsIgnoreCase("getMarketMovers"))
		{
			String strSymbol = ls.get(1).toString();

			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			atSymbol.symbolType = ATSymbolType.TopMarketMovers;
			atSymbol.exchangeType = (byte)ls.get(2).toString().getBytes()[0];
			
			List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
			lstSymbols.add(atSymbol);
			long request = apiSession.GetRequestor().SendATMarketMoversDbRequest(lstSymbols, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			
			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}
		
		/**********************************************************************
		 * //subscribeMarketMovers | unsubscribeMarketMovers
		 * Example: subscribing/unsubscribing to Net-Gainers on Nasdaq exchange ( NG Q):
		 * 		subscribeMarketMovers NG Q
		 * 		unsubscribeMarketMovers NG Q
		 **********************************************************************/

		else if(count >= 2 && ( ((String)ls.get(0)).equalsIgnoreCase("subscribeMarketMovers") ||
								((String)ls.get(0)).equalsIgnoreCase("unsubscribeMarketMovers")))
		{
			String strSymbol = ls.get(1).toString();
			ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbol);
			atSymbol.symbolType = ATSymbolType.TopMarketMovers;
			atSymbol.exchangeType = (byte)ls.get(2).toString().getBytes()[0];
				
			ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
			requestType.m_streamRequestType = ((String)ls.get(0)).equalsIgnoreCase("subscribeMarketMovers") ? 
												ATStreamRequestType.StreamRequestSubscribe : ATStreamRequestType.StreamRequestUnsubscribe;
			
			List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
			lstSymbols.add(atSymbol);
									
			long request = apiSession.GetRequestor().SendATMarketMoversStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			
			System.out.println("SEND " + request + ": " + ls.get(0).toString() + " request [" + strSymbol + "]");
			if(request < 0)
			{
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
			}
		}
		
		/**********************************************************************
		 * //subscribeQuoteStream | unsubscribeQuoteStream
		 * Example:
		 * Single symbol request:
		 * 		subscribeQuoteStream  AAPL
		 * 		unsubscribeQuoteStream  AAPL
		 * Multiple symbol request:
		 * 		subscribeQuoteStream  AAPL,AMZN
		 * 		unsubscribeQuoteStream  AAPL,AMZN
		 **********************************************************************/
		else if(count >= 2 && ( ((String)ls.get(0)).equalsIgnoreCase("subscribeQuoteStream") ||
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
		 * 		StreamRequestSubscribeQuotesOnly  AAPL
		 * 		StreamRequestUnsubscribeQuotesOnly  AAPL
		 * Multiple symbol request:
		 * 		StreamRequestSubscribeQuotesOnly  AAPL,AMZN
		 * 		StreamRequestUnsubscribeQuotesOnly  AAPL,AMZN
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
		}else if (count == 1  && ( ((String)ls.get(0)).equalsIgnoreCase("update"))){
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
		 * 		subscribeTradesOnlyQuoteStream  AAPL
		 * 		unsubscribeTradesOnlyQuoteStream  AAPL
		 * Multiple symbol request:
		 * 		subscribeTradesOnlyQuoteStream  AAPL,AMZN
		 * 		unsubscribeTradesOnlyQuoteStream  AAPL,AMZN
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

	
	public void run() {
            
		ArrayList<String[]> lRet = new ArrayList<String[]>();
        String[] rData = new String[5];
        
        serverapi = new ActiveTickServerAPI();	      
	      apiSession = new APISession(serverapi);
	      serverapi.ATInitAPI();
	    
        String atHostName = "activetick1.activetick.com";
        int atPort = 443;
        String guid = "80af4953bb7f4dcf85523ad332161eff";
        String userId = "liangcai";
        String password = "S@^@nt932456";
        
        ATGUID atguid = (new ATServerAPIDefines()).new ATGUID();
        atguid.SetGuid(guid);
        
        boolean rc = apiSession.Init(atguid, atHostName, atPort, userId, password, map);
        System.out.println("\ninit status: " + (rc == true ? "ok" : "failed"));
	      
 
        try{

            System.out.println("Socket accepted");
                
            while(true){   
                
                InputStream is = socket.getInputStream();
                
                if (is.available() != 0 ){
                    
                    InputStreamReader isr = new InputStreamReader(is);
                    
                    BufferedReader br1 = new BufferedReader(isr);
                    try 
      		      {  
                    String jstr = br1.readLine();
                    
                    System.out.println("Message received from client is "+jstr);
                    
			         if(jstr.length() > 0)
			         {
			        	 if(jstr.startsWith("quit"))
			        		 break;
			        	 
                            String returnMessage =  "hi";
                   
                           Object oObj=JSONValue.parse(jstr);
                        
                       
                        JSONObject obj = (JSONObject) oObj;
                        
                        JSONObject req  = (JSONObject)obj.get("request");
                        
                        String cmd = (String)req.get("command");
                        String cl = (String)req.get("client");
                        
                        String sbList = (String)req.get("symlist");
                        String cmdStr;
                        if (sbList.contains(",")){
                        	JSONArray sList = (JSONArray)req.get("symlist");
                        	
                        	Iterator<String> iterator = sList.iterator();
                        	cmdStr = iterator.next();
                        	while(iterator.hasNext()){  
                        	   cmdStr =  "," + iterator.next();
                        	}
                        }else{
                        	cmdStr = sbList;
                        }
                        
                        cmd = cmd + " " + cmdStr;
                        
                        processInput(cmd);
			         }
			  } 
		      catch (Exception e) 
			  {
		    	  System.out.println("IO error trying to read your input!");
			  }
	      }
        }
	      apiSession.UnInit();
	      serverapi.ATShutdownAPI();
           
	      
        }catch (Exception e) 
        {
            e.printStackTrace();
        }
        finally
        {
            try
            {
                socket.close();
        System.out.println("Socket CLosed");
            }
            catch(Exception e){}
        }
    }
}


}
           