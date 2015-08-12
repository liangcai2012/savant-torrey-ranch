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
import java.text.SimpleDateFormat;

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

import org.json.JSONObject;
import org.json.JSONException;


public class StreamerRun 
{
	private final int POOL_SIZE = 10;
	private ExecutorService m_exService;
	private ServerSocket m_serverSocket;

	public static ActiveTickServerAPI serverapi;
	public static APISession apiSession;

	public class Client{
		public int interval;
		public int	maMask;
		public int	barMask;
		public ArrayList<String> symList; 
		public long lastSecond;
		public String delayedTicks;
		
		public Client(ArrayList<String> symbols){
			symList = symbols;
			interval = -1;
			maMask = 0;
			barMask = 0;
			lastSecond = -1;
			delayedTicks="";
		}
	}

	public HashMap<String, Client> m_clientMgr; //status data per client:w
	public HashMap <String, SymData> m_symDataMap;//SymData per symbol

	//this is a time gap between Streamer's system clock and timestamp received in tick data. This value is set when first tick data is received and never changed. 
	public long m_atTimeGap=-1;

	public StreamerRun() 
	{
	   	serverapi = new ActiveTickServerAPI();
		apiSession = new APISession(serverapi);

		//init data structure
	 	m_clientMgr= new HashMap<String, Client>();
		m_symDataMap = new HashMap <String, SymData>();
  	}

  	public boolean Init() throws IOException, InterruptedException{

        SavantConfig config = SavantConfig.getConfig();
        //String hostName = "localhost";
        String hostName = config.getProperty("STREAMER_HOST"); 
        int port = Integer.parseInt(config.getProperty("STREAMER_PORT"));

    	//initialize the api and login to the service
	   	serverapi.ATInitAPI();

        String atHostName = config.getProperty("AT_HOSTNAME");
        int atPort = Integer.parseInt(config.getProperty("AT_PORT"));
        String guid = config.getProperty("AT_GUID");
        String userId = config.getProperty("AT_USER");
        String password = config.getProperty("AT_PASSWORD");

		ATGUID atguid = (new ATServerAPIDefines()).new ATGUID();
		atguid.SetGuid(guid);

		boolean rc = apiSession.Init(atguid, atHostName, atPort, userId, password, this);
		System.out.println("init status: " + (rc ? "ok" : "failed"));
		if (!rc)
	       		return false;
	    Thread.sleep(2000);
	        /*	if(!apiSession.m_loginSucceed){
	        	System.out.println("Login failed!");
	         	return false;
	      	}*/

     //initialize the server socket
		InetAddress bindAdd = InetAddress.getByName(hostName);
		m_serverSocket = new ServerSocket(port, 100, bindAdd);
		int totalNum = Runtime.getRuntime().availableProcessors()*POOL_SIZE;
		System.out.println("Pool size:" + String.valueOf(totalNum));
		m_exService = Executors.newFixedThreadPool(totalNum);		
		System.out.println("Server Started.....");
     		return true;
	}


	public void acceptClient()
	{	
		while (true){
        	Socket socket = null;
			try{
	       		socket = m_serverSocket.accept();
		   		//System.out.println("ready for next client");
	       		m_exService.execute(new CmdHandler(socket, this));
			} 
		    catch (Exception e){
		   		e.printStackTrace();
		   	}	 		
     	}		
	}
	
	public String second2ts(long second)
	{
  		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMddHHmmss"); 
  		dateFormat.setTimeZone(TimeZone.getTimeZone("EST5EDT")); 
  		return dateFormat.format(new Date(second*1000));

	}
  	
	public static void main(String[] args) throws IOException, InterruptedException 
  	{		
     	StreamerRun sr = new StreamerRun();
     	if (sr.Init()){
        	sr.acceptClient();
			apiSession.UnInit();
			serverapi.ATShutdownAPI();
     	}
     	else{
   	  		System.out.println("Fail to initialize Streamer. Exiting");
   	  		System.exit(-1);
     	}
  	}
}
		 
