//import JavaToJson;

package atapi.wrapper;

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

	public	HashMap<String, ArrayList<String>> m_clientSymMap;
	public HashMap <String, ArrayList<String[]>> m_tickDataMap;
	public HashMap<String, Integer> m_symRefMap; 
	public HashMap <String, SymData> m_symDataMap;
	public HashMap <String, DelayedTicks> m_symDelayMap;
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
	 	m_tickSymMap = new HashMap<String, ArrayList<String[]>>();
		m_symRefMap = new HashMap<String, Integer>();
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

		boolean rc = apiSession.Init(atguid, atHostName, atPort, userId, password, this);
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
	         		exService.execute(new CmdHandler(socket, this));
			} 
		        catch (Exception e){
		      		e.printStackTrace();
		   	}	 		
      		}		
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
