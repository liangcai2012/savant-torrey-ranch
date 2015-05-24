import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import com.sun.jmx.snmp.Timestamp;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.Helpers;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATSYMBOL;
import at.shared.ATServerAPIDefines.ATStreamRequestType;
import at.utils.jlib.Errors;

class CmdHandler implements Runnable{
	private Socket socket;
	private StreamerRun sr;
	public static ActiveTickServerAPI serverapi;
    public static APISession apiSession;

	 
	public CmdHandler(Socket socket, StreamerRun srun)		 {
		this.socket = socket;
		this.sr = srun;
        //[Liang] we should not create a new api session here. This is already done. Please change sr.apisession to public or package and use it. 
		serverapi = new ActiveTickServerAPI();	      
	     apiSession = new APISession(serverapi);
	     serverapi.ATInitAPI();
	}

	//TODO: return values
   	public void run() 
	{
		//ArrayList<String[]> lRet = new ArrayList<String[]>();
		//String[] rData = new String[5];
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
						if(jstr.length() > 0)
						{
                //is this part of the specification? Streamer is a server shared by multiple clients so it should not be shutdown by one client
				//			if(jstr.startsWith("quit"))
				//				break;
							String returnMessage =	"hi";
							JSONParser parser = new JSONParser();
							//Object oObj=JSONValue.parse(jstr);
							Object oObj;
							long getTime = System.currentTimeMillis();
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
									processSubscribe(client, (List<String>)symlist);
									//if(!processSubscribe(client, (List<String>)symlist))
									//	System.out.println("Error = " + Errors.GetStringFromError((int)request));
										
								}
								else if (cmd.equalsIgnoreCase("unsubscribe"))
								{
									String client = (String)req.get("client");
									processUnsubscribe(client);   	                            	
								}
								else if(cmd.equalsIgnoreCase("update"))
								{
									String client = (String)req.get("client");
									String interval = (String)req.get("interval");
									String bar_mask = (String)req.get("bar_mask");
									String ma_mask = (String)req.get("ma_mask");
									int bar_mask_num = maskConvert(bar_mask, 6);
									if(bar_mask_num == -1){
        								System.out.println("received request is not a valid json input: " +jstr);
        								continue;
        							}
									int ma_mask_num = maskConvert(ma_mask, 9);
									if(ma_mask_num == -1){
        								System.out.println("received request is not a valid json input: " +jstr);
        								continue;
        							}
									
									processUpdate(client, Integer.parseInt(interval), getTime, bar_mask_num, ma_mask_num);   	                            	
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

   	
   	// TODO Auto-generated method stub
   	//convert mask of string value (eg. "111111") into a binary value (0x11111), 
   	//param: 
	/**************
	 * //mask_convert
	 * @param mask: string value of mask
	 * @param len: length of the string, can only be 6 (for bar mask) or 9 (for ma mask)
	 * @return binary value of the mask
	 * convert mask of string value (eg. "111111") into a binary value (0x11111), 
	 */
	private int maskConvert(String mask, int len) {
		return 0;
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
	public void processSubscribe(String client, List<String> symlist)
	{
		//
		ArrayList<String> newAddSymlist = new ArrayList<String>();
		
		// if client doesn't exist, create.
		if(sr.m_clientSymMap.get(client) == null){
			sr.m_clientSymMap.put(client,  new ArrayList<String>());
		}
		
		//if client existed, check syms of this client existed or not
		//add those not existed sym to newAddSymlist
		//SymData exsymlist = sr.m_symDataMap.get(client);
		ArrayList<String> exsymlist = sr.m_clientSymMap.get(client);
		for (String sym : symlist) {
			if(!exsymlist.contains(sym)){
				exsymlist.add(sym);
				newAddSymlist.add(sym);
				//sr.m_symDataMap.put(sym, new SymData());
			}
		}
		//[Liang:] The symbol is not subscribed for this client does not necessarily mean it is not subscribed yet. It can be previously subscribed for another client. And we should not subscribe it again if so. For this we need add a public array of all symbols that we can subscribed. StreamerRunner should be maintaining this array. Once we get a new subscribe request, we need to check here whether this symbol is in the list, if so we only need to add it to m_clientSymMap; otherwise we need to call ATAPI to subscribe it as well. This logic should also affect handler of client unsubscribe. 
  
	    
		//subscribe syms in newAddSymlist
			List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();

			if(!newAddSymlist.isEmpty() && !newAddSymlist.contains(","))
			{
				for(String strSymbols : newAddSymlist){
					ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbols);
					lstSymbols.add(atSymbol);
				}			
			
			ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
			requestType.m_streamRequestType = ATStreamRequestType.StreamRequestSubscribeTradesOnly ;
			
			long request = apiSession.GetRequestor().SendATQuoteStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			if(request < 0)
			{
				// or throw an exception?
				System.out.println("Error = " + Errors.GetStringFromError((int)request));
				//return false;
			}
		}
		
		//return true;
	}	
	
	
	/***************
	 * 
	 * @param client: client name
	 * @return response in json
	 */
	//? what if some syms in this client also exist in other client' list?
	public void processUnsubscribe(String client)
	{
		//if client does not exist, return false;
		if(sr.m_clientSymMap.containsKey(client)){ 
		
		//if client exists, remove its symlist from map 
		List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
		ArrayList<String> exsymlist = sr.m_clientSymMap.get(client);
		
		//remove symlist for client
		sr.m_clientSymMap.remove(client);
		
		if(!exsymlist.isEmpty())
		{
			for(String strSymbols : exsymlist){
				ATSYMBOL atSymbol = Helpers.StringToSymbol(strSymbols);
				lstSymbols.add(atSymbol);
			}			
		
		ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
		requestType.m_streamRequestType = ATStreamRequestType.StreamRequestUnsubscribeTradesOnly ;
		
		long request = apiSession.GetRequestor().SendATQuoteStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
		if(request < 0)
		{
			// or throw an exception?
			System.out.println("Error = " + Errors.GetStringFromError((int)request));
			//return false;
		}
	}
	
	//return true;
		
		}
	}
	
	/****************
	 * 
	 * @param client: client name
	 * @param interval: must be one value in ["1s", "5s", "10s", "30s", "1m", "5m", "10m", "30m", "1h"]
	 * @param bar_mask: 6 digits with 0 and 1
	 * @param ma_mask: 9 digits with 0 and 1
	 * @return
	 */
	public String processUpdate(String client, int interval,long second, int bar_mask, int ma_mask)
	{
		 String ret = null;
	     ArrayList<String> symDataList = sr.m_clientSymMap.get(client);
	     for(String sym : symDataList){
	    	 SymData sd = sr.m_symDataMap.get(sym);
	    	  ret = sd.getBar( second, interval, bar_mask);
	     }
	     return ret;

	//[Liang] This is a common error, you only return the bar data of last symbol in the list. You need to encode them into one json response. 
	}
	     
	     
}
