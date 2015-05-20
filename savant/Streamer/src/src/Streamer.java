package atapi.wrapper;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.ActiveTickStreamListener;
import at.feedapi.Session;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATGUID;
import at.utils.jlib.PrintfFormat;

public class Streamer extends ActiveTickStreamListener
{
	 
	APISession m_session;
	
	private final static int ARRAY_SIZE = 3600;
	
	private long tPrice = 0;
	private long tSize = 0;
	private long sTime = 0;
	int i = 0;
	private int sec = 60;
	private int min = 60;
	private StreamerRun sr;
	
	private long preVol;
	private double prePri;
	
	private DelayedTicks dt = new DelayedTicks();
	
	public Streamer(APISession session,  StreamerRun sr)
	{
		super(session.GetSession(), false);
		m_session = session;
		this.sr = sr;
		 

		   
	}
	
	public void init(String guid, String atHostName, int atPort, String userId, String password, StreamerRun sr){
		/*String atHostName = "activetick1.activetick.com";
		          int atPort = 443;
		          String guid = "80af4953bb7f4dcf85523ad332161eff";
		          String userId = "liangcai";
		          String password = "S@^@nt932456";
		 */
		          ATGUID atguid = (new ATServerAPIDefines()).new ATGUID();
		          atguid.SetGuid(guid);
		 
		          boolean rc = m_session.Init(atguid, atHostName, atPort, userId, password, sr);
		          System.out.println("init status: " + (rc ? "ok" : "failed"));

	}
	
	public void OnATStreamTradeUpdate(ATServerAPIDefines.ATQUOTESTREAM_TRADE_UPDATE update)
	{		
		
		  
		String strSymbol = new String(update.symbol.symbol);
		int plainSymbolIndex = strSymbol.indexOf((byte)0);
		strSymbol = strSymbol.substring(0, plainSymbolIndex);
		int timeGap = 0;
		StringBuffer sb = new StringBuffer();
		//sb.append("[");
		if(sr.m_symDataMap.get(strSymbol) == null){
			sr.m_symDataMap.put(strSymbol,  new SymData());
		}
		
		SymData sd = sr.m_symDataMap.get(strSymbol);
		
		long tTime = update.lastDateTime.hour * 1000 + update.lastDateTime.minute * 100 + update.lastDateTime.second;
		
		String strFormat = "%0." + update.lastPrice.precision + "f";
		String sPrice = new PrintfFormat(strFormat).sprintf(update.lastPrice.price);
		Double lPrice = Double.parseDouble(sPrice);
		
		long size = update.lastSize;
		//check if there is delay
		
		if (sTime == 0){
			sTime = tTime;
		}
		//System.out.println("hehhehe  sTime is" + sTime);
		if(sTime != tTime) System.out.println("time changed!!! privous is" + sTime + "now is" + tTime);
		if(sec == 60) sec = update.lastDateTime.second;
		if(min == 60) min = update.lastDateTime.minute;

		dt.onDelayedTick(sTime, tTime, preVol, prePri);
		
		
						
		if (dt.onBarRequest(tTime) != null){
			sd = dt.onBarRequest(tTime);
		}else{
			sd.update(tTime, size, lPrice, 0);
		}
		sr.m_symDataMap.put(strSymbol, sd);
		
		preVol = size;
	    prePri = lPrice;
		
		
		/*
		sb.append(update.lastDateTime.hour);
		sb.append(":");
		sb.append(update.lastDateTime.minute);
		sb.append(":");
		sb.append(update.lastDateTime.second);
		//sb.append(":");
		String tTime = update.lastDateTime.hour +":" + update.lastDateTime.minute +":" + update.lastDateTime.second;
		
		
		if (sTime == null){
			sTime = tTime;
		}
		//System.out.println("hehhehe  sTime is" + sTime);
		if(!sTime.equals(tTime)) System.out.println("time changed!!! privous is" + sTime + "now is" + tTime);
		if(sec == 60) sec = update.lastDateTime.second;
		if(min == 60) min = update.lastDateTime.minute;
		
		//sb.append(update.lastDateTime.milliseconds);
		//sb.append("] STREAMTRADE [symbol:");
		sb.append(strSymbol);
		sb.append(" last:");
		
		String strFormat = "%0." + update.lastPrice.precision + "f";
		String sPrice = new PrintfFormat(strFormat).sprintf(update.lastPrice.price);
	
		Double lPrice = Double.parseDouble(sPrice);
		
		sb.append(new PrintfFormat(strFormat).sprintf(update.lastPrice.price));
		
		sb.append(" lastSize:");
		sb.append(update.lastSize);	
		long size = update.lastSize;
		sb.append("]");
		System.out.println(sb.toString());

		
		
	    if(tTime.equals(sTime)){
			tPrice += lPrice*size;
			tSize += size;	
			System.out.println("add to size.....");
		}else{
			String[] each = new String[5];
			each[0] = strSymbol;
			each[1] = sTime;
			each[2] =  tPrice + "";
			each[3] =  tSize + "";
			each[4] = ((double)tPrice/(double)tSize) + "";
				if(map.get(strSymbol) == null){
					//
				// String[][] aRR = new String[ARRAY_SIZE][3];
					ArrayList<String[]> aPrice = new ArrayList<String[]>(); 
					//aPrice.add(each);
					//System.out.println("each is" + aPrice.get(0));
					System.out.println("add" + strSymbol + "to map");
					map.put(strSymbol, aPrice);     
				}else {
					if(map.get(strSymbol).size() == ARRAY_SIZE){
						System.out.println("remove 1");
						map.get(strSymbol).remove(0);
						System.out.println("size is " + map.get(strSymbol).size());// save to another arrayList 
					}
				}
				    System.out.println("now add is " + strSymbol);
					map.get(strSymbol).add(each);
					System.out.println("then size is " + map.get(strSymbol).size());
				
					timeGap = update.lastDateTime.second - sec;
					System.out.println("timeGap is"+ timeGap);
					if(timeGap < 0) {
						int minGap = update.lastDateTime.minute - min;
						timeGap = 60*minGap+ timeGap;
						System.out.println("new timeGap is"+ timeGap);
					}
					
					if (timeGap > 1){
						System.out.println("hehehe timeGap > 1");
						
					
						ArrayList<String[]> last = map.get(strSymbol);
						//new
						int reSec = 0;
						int reMin = 1;
						String[] preEach = last.get(last.size() - 1);
						System.out.println("pre Time is" + preEach[1]);
						
						int preSec = Integer.parseInt(preEach[1].split(":")[2]);
						System.out.println("get Sec" + preSec);
						//int preMin = Integer.parseInt(preEach[1].substring(preEach[1].length()-3, 2));
						int preMin = Integer.parseInt(preEach[1].split(":")[1]);
						System.out.println("get Min" + preMin);
						for(int t = 0; t < timeGap-1; t++){
							String[] newArr = new String[5];
							newArr[0] = preEach[0];
							newArr[1] = preEach[1];
							newArr[2] = preEach[2];
							newArr[3] = preEach[3];
							newArr[4] = preEach[4];
						  int count = preSec;
							if(count < 59){
								preSec += 1;
							       newArr[1] = newArr[1].split(":")[0]+ ":" + newArr[1].split(":")[1] + ":" + preSec;
							       
							}else{
								System.out.println("reSec is " + reSec);
								if(reSec > 59){
									reMin = reMin+1;
									reSec = 0;
								}
								 newArr[1] = newArr[1].split(":")[0] + ":"+ (preMin + reMin) +":"+ reSec;
								    reSec++;
								
						    }
							
							System.out.println("now  pre Time is" + newArr[1]);
							map.get(strSymbol).add(newArr);
							System.out.println("ArrayList Size is " + map.get(strSymbol).size());
							System.out.println("add a previous value!!!" + newArr[1] + " " + newArr[2]);
						}
					}
			  
			  sTime = tTime;
			  tPrice = (long) (lPrice*size);
			  tSize = size;
			  i++;
			  String oldTime = sTime;
				sec = Integer.parseInt(oldTime.split(":")[2]);
				min = Integer.parseInt(oldTime.split(":")[1]);
			  System.out.println("sec is" + sec);
			}
		}
		
		
		// if cmd = update
		
		//read data, write into Output Stream
		
	*/	
	}	
	
	
	public HashMap<String, SymData> getSymMap(){
		return this.sr.m_symDataMap;
	}
	
	public void OnATStreamQuoteUpdate(ATServerAPIDefines.ATQUOTESTREAM_QUOTE_UPDATE update) 
	{
		

		String strSymbol = new String(update.symbol.symbol);
		int plainSymbolIndex = strSymbol.indexOf((byte)0);
		strSymbol = strSymbol.substring(0, plainSymbolIndex);
		StringBuffer sb = new StringBuffer();
		sb.append("[");
		sb.append(update.quoteDateTime.hour);
		sb.append(":");
		sb.append(update.quoteDateTime.minute);
		sb.append(":");
		sb.append(update.quoteDateTime.second);
		sb.append(":");
		sb.append(update.quoteDateTime.milliseconds);
		sb.append("] STREAMQUOTE [symbol:");
		sb.append(strSymbol);
		sb.append(" bid:");
		String strFormat = "%0." + update.bidPrice.precision + "f";
		sb.append(new PrintfFormat(strFormat).sprintf(update.bidPrice.price));
		sb.append(" ask:");
		strFormat = "%0." + update.askPrice.precision + "f";
		sb.append(new PrintfFormat(strFormat).sprintf(update.askPrice.price));
		sb.append(" bidSize:");
		sb.append(update.bidSize);
		sb.append(" askSize:");
		sb.append(update.askSize);
		sb.append("]");
		//System.out.println(sb.toString());	
	}

	public void OnATStreamTopMarketMoversUpdate(ATServerAPIDefines.ATMARKET_MOVERS_STREAM_UPDATE update) 
	{
		String strSymbol = new String(update.marketMovers.symbol.symbol);
		int plainSymbolIndex = strSymbol.indexOf((byte)0);
		strSymbol = strSymbol.substring(0, plainSymbolIndex);
		StringBuffer sb = new StringBuffer();
		sb.append("RECV: [");
		sb.append(update.lastUpdateTime.hour);
		sb.append(":");
		sb.append(update.lastUpdateTime.minute);
		sb.append(":");
		sb.append(update.lastUpdateTime.second);
		sb.append(":");
		sb.append(update.lastUpdateTime.milliseconds);
		sb.append("] STREAMMOVERS [symbol:");
		sb.append(strSymbol);
		sb.append("]");
		System.out.println(sb.toString());
		
		String strFormat = "";
		for(int i = 0; i < update.marketMovers.items.length; i++)
		{
			StringBuilder sb2 = new StringBuilder();
			String strItemSymbol = new String(update.marketMovers.items[i].symbol.symbol);
			int plainItemSymbolIndex = strItemSymbol.indexOf((byte)0);
			strItemSymbol = strItemSymbol.substring(0, plainItemSymbolIndex);

			sb2.append("symbol:");
			sb2.append(strItemSymbol);
			
			strFormat = "%0." + update.marketMovers.items[i].lastPrice.precision + "f";
			sb2.append("  \t[last:" + new PrintfFormat(strFormat).sprintf(update.marketMovers.items[i].lastPrice.price));
			
			sb2.append(" volume:");
			sb2.append(update.marketMovers.items[i].volume);
			System.out.println(sb2.toString());
		}
		
		System.out.println("-------------------------------------------------------");
	}
}

