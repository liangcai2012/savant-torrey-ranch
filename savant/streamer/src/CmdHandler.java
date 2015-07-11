import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.IOException;

import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.text.SimpleDateFormat;

//import org.json.simple.JSONArray;
//import org.json.simple.JSONObject;
//import org.json.simple.parser.JSONParser;
//import org.json.simple.parser.ParseException;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.Helpers;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATSYMBOL;
import at.shared.ATServerAPIDefines.ATStreamRequestType;
import at.utils.jlib.Errors;

class CmdHandlerException extends Exception {
    public CmdHandlerException(String message) {
        super(message);
    }
}

class CmdHandler implements Runnable{
	private Socket socket;
	private StreamerRun sr;

	 
	public CmdHandler(Socket s, StreamerRun srun)		 {
		socket = s;
		sr = srun;
	}

   	public void run() 
	{
		String jstr="";
		try{
			InputStream is = socket.getInputStream();
			InputStreamReader isr = new InputStreamReader(is);
			BufferedReader br1 = new BufferedReader(isr);
			jstr = br1.readLine();
			JSONObject resp=null;
			long seconds = System.currentTimeMillis()/1000;
			String errMsg="";
			JSONObject obj = new JSONObject(jstr);
			JSONObject req	= obj.getJSONObject("request");
			String cmd = req.getString("command");
			String client = req.getString("client");
			//System.out.println("Command (" + cmd + ") received from " + client);
			if (cmd.equalsIgnoreCase("subscribe"))
			{
				JSONArray symlist = req.getJSONArray("symlist");
				ArrayList<String> syms = new ArrayList<String>();
				for(int i=0; i<symlist.length(); i++)
					syms.add(symlist.getString(i));
				resp = processSubscribe(client, syms);
			}
			else if (cmd.equalsIgnoreCase("unsubscribe"))
			{
				resp = processUnsubscribe(client);   	                            	
			}
			else if(cmd.equalsIgnoreCase("update"))
			{
				String interval = ""; 
				if(req.has("interval"))
					interval = req.getString("interval");
				String bar_mask = "";
				if(req.has("bar_mask"))
					bar_mask = req.getString("bar_mask");
				String ma_mask = ""; 
				if(req.has("ma_mask"))
					ma_mask = req.getString("ma_mask");
				resp= processUpdate(client, interval, seconds, bar_mask, ma_mask);   	                            	
			}
			else{
				resp= new JSONObject();
				resp.put("errcode", new Integer(-1));
				resp.put("errMsg", "Invalid command: " + cmd);
			}
				
			JSONObject outer = new JSONObject();
			outer.put("response", resp);
            BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
            out.write(outer.toString());
            out.flush();
            socket.close();
		}
		catch(JSONException je){
			System.out.println("received request is not a valid json input: " +jstr);
		}
		catch(java.lang.ClassCastException e){
			System.out.println("received json request contains invalid field type: " +jstr);
		}
		catch (Exception e) {
		   	System.out.println("Unknown exception. Program still running. Error:" + e.getMessage());
			e.printStackTrace();
		}
		finally{
			try{
		   		socket.close();
			}
			catch(IOException e){
				System.out.println("Fail to close socket: " + e.getMessage());
			}
		}
	}

   	
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
		int ret = 0; 
		if(mask.length() < len){
			System.out.println("Length of mask string not equal to specified value");
			return -1;
		}
		for(int i=1;i<=len;i++){
			if('1' == mask.charAt(len-i))
				ret += 1<<i;
		}
		return ret;
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
	public JSONObject processSubscribe(String client, ArrayList<String> symlist)
	{
		List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
		SymData sd;
		String errMsg = "";
		JSONObject innerResp = new JSONObject();
		// if client doesn't exist, create it.
		do{
			if(!sr.m_clientMgr.containsKey(client)){
				sr.m_clientMgr.put(client,  sr.new Client(symlist));
			}
			
			//if client existed, check syms of this client existed or not
			//add those not existed sym to newAddSymlist
			//SymData exsymlist = sr.m_symDataMap.get(client);
			for (String sym : symlist) {
				if(!sr.m_symDataMap.containsKey(sym)){
					ATSYMBOL atSymbol = Helpers.StringToSymbol(sym);
					lstSymbols.add(atSymbol);
					sd = new SymData(); 
					sr.m_symDataMap.put(sym, sd);
				}
				else{
					sd = sr.m_symDataMap.get(sym);
				}
				sd.addClient(client);
			}
			if(!lstSymbols.isEmpty()){
				//subscribe syms in newAddSymlist
				ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
				requestType.m_streamRequestType = ATStreamRequestType.StreamRequestSubscribeTradesOnly ;
				long request = sr.apiSession.GetRequestor().SendATQuoteStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
				if(request < 0)
				{
					errMsg = "Fail to subscribe symbols: " + Errors.GetStringFromError((int)request);
					break;
				}
			}
			try{
				innerResp.put("errcode", new Integer(0));
			}
			catch(JSONException e){
				System.out.println("Fail to create response: " + e.getMessage());
			}
			return innerResp;
		}while(false);
		try{
			innerResp.put("errcode", new Integer(-1));
			innerResp.put("errMsg", errMsg);
		}
		catch(JSONException e){
			System.out.println("Fail to create response: " + e.getMessage());
		}
		System.out.println(errMsg);
		return innerResp;
	}	
	
	
	/***************
	 * 
	 * @param client: client name
	 * @return response in json
	 */
	//? what if some syms in this client also exist in other client' list?
	public JSONObject processUnsubscribe(String client)
	{
		SymData sd;
		String errMsg = "";
		List<ATSYMBOL> lstSymbols = new ArrayList<ATSYMBOL>();
		JSONObject innerResp = new JSONObject();
		do{
			if(!sr.m_clientMgr.containsKey(client)){
				errMsg = "Client " + client + " has not been subscribed!";
				break;
			}
			StreamerRun.Client c =  sr.m_clientMgr.get(client);
			for(String sym:c.symList){
				if(sr.m_symDataMap.containsKey(sym)){
					sd = sr.m_symDataMap.get(sym);
					sd.delClient(client);
					if(sd.ifNoClient()){
						ATSYMBOL atSymbol = Helpers.StringToSymbol(sym);
						lstSymbols.add(atSymbol);
						sr.m_symDataMap.remove(sym);	
					}
				}
			}
			sr.m_clientMgr.remove(client);
			ATStreamRequestType requestType = (new ATServerAPIDefines()).new ATStreamRequestType();
			requestType.m_streamRequestType = ATStreamRequestType.StreamRequestUnsubscribeTradesOnly ;
			
			long request = sr.apiSession.GetRequestor().SendATQuoteStreamRequest(lstSymbols, requestType, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
			if(request < 0)
			{
				errMsg = "Fail to unsubscribe symbols: " + Errors.GetStringFromError((int)request);
				break;
			}
			try{
				innerResp.put("errcode", new Integer(0));
			}
			catch(JSONException e){
				System.out.println("Fail to create response: " + e.getMessage());
			}
			return innerResp;
		}while(false);
		try{
			innerResp.put("errcode", new Integer(-1));
			innerResp.put("errMsg", errMsg);
		}
		catch(JSONException e){
			System.out.println("Fail to create response: " + e.getMessage());
		}
		System.out.println(errMsg);
		return innerResp;
	}
	
	/****************
	 * 
	 * @param client: client name
	 * @param interval: must be one value in ["1s", "5s", "10s", "30s", "1m", "5m", "10m", "30m", "1h"]
	 * @param bar_mask: 5 digits with 0 and 1
	 * @param ma_mask: 9 digits with 0 and 1
	 * @return
	 */
	public JSONObject processUpdate(String client, String interval,long second, String bar_mask, String ma_mask)
	{
		String errMsg = "";
		StreamerRun.Client c;
		boolean changeMask = false;
		JSONObject innerResp = new JSONObject();
		do{
			if(!sr.m_clientMgr.containsKey(client)){ 
				errMsg = "Client " + client + " has not been subscribed!";
				break;
			}
			c =  sr.m_clientMgr.get(client);
			if(interval.length() ==0){
				if(c.interval == -1){
					errMsg="No interval value specified for client: " + client;
					break;
				}
			}
			else{
				int nInterval = SymData.getInterval(interval);
				if(nInterval == -1){
					errMsg="Invalid interval value: " + interval;
					break;
				}
				c.interval = nInterval;
			}	
			if(bar_mask.length() !=0){
				int nBarMask = maskConvert(bar_mask, 5);
				if (nBarMask == -1){
					errMsg="Invalid bar mask value: " + bar_mask;
					break;
				}
				//simply does nothing
				c.barMask = nBarMask;
			}
			if(ma_mask.length() !=0){
				int nMaMask = maskConvert(ma_mask, 9);
				if (nMaMask== -1){
					errMsg="Invalid bar mask value: " + ma_mask;
					break;
				}
				if(c.maMask != nMaMask){
					c.maMask = nMaMask;
					changeMask = true;
				}
			}
			try{
				JSONArray dataArray = new JSONArray();
				innerResp.put("client", client);
				innerResp.put("timestamp", sr.second2ts(second));
				innerResp.put("interval", interval); 
	     		for(String sym : c.symList){
					SymData sd = sr.m_symDataMap.get(sym);
					JSONObject dataObj = new JSONObject();
					dataObj.put("symbol", sym);

					//change mask if needed
					if(changeMask){
						int newMask = 0;
						for(String cl: sd.getClients()){
							newMask = newMask| sr.m_clientMgr.get(cl).maMask;
						}
						sd.changeMA(newMask);
					}
					//get bar
	     		    String strBar = sd.getBar(second, c.interval, c.barMask);
					dataObj.put("bar", strBar);
					//get ma
					if(c.maMask != 0){
						String strMa = sd.getMA(c.interval, c.maMask);
						dataObj.put("ma", strMa);
					}
					//get delayed
					if(c.delayedTicks.length() >0){
						dataObj.put("delay", c.delayedTicks);
						c.delayedTicks = "";
					}
					dataArray.put(dataObj);
	     		} 
				//set lastSeconds
				c.lastSecond = second;
				innerResp.put("data", dataArray);
			}
			catch(JSONException e){
				System.out.println("Fail to create response: " + e.getMessage());
			}
			return innerResp;
		}while(false);		
		try{
			innerResp.put("errcode", new Integer(-1));
			innerResp.put("errMsg", errMsg);
		}
		catch(JSONException e){
			System.out.println("Fail to create response: " + e.getMessage());
		}
		System.out.println(errMsg);
		return innerResp;
	}
}
