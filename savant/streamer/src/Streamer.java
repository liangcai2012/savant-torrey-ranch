import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Date;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.ActiveTickStreamListener;
import at.feedapi.Session;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATGUID;
import at.utils.jlib.PrintfFormat;

public class Streamer extends ActiveTickStreamListener
{
	 
	private APISession m_session;
	private StreamerRun m_sr;
	
	private long tPrice = 0;
	private long tSize = 0;
	private long sTime = 0;
	private int sec = 60;
	private int min = 60;
	
	private long preVol;
	private double prePri;
	
	
	public Streamer(APISession session,  StreamerRun srun)
	{
		super(session.GetSession(), false);
		m_session = session;
		m_sr = srun;
	}
	
	public void OnATStreamTradeUpdate(ATServerAPIDefines.ATQUOTESTREAM_TRADE_UPDATE update)
	{		
		long start = System.currentTimeMillis();
		String symbol = new String(update.symbol.symbol);
		int plainSymbolIndex = symbol.indexOf((byte)0);
		if(plainSymbolIndex >0)
			symbol = symbol.substring(0, plainSymbolIndex);
		Double price = update.lastPrice.price; 
		long vol = update.lastSize;
		SymData sd = m_sr.m_symDataMap.get(symbol);
		if(sd == null){
			System.out.println("Receiving tick data of unexpected symbol: " + symbol);
			return;
		}

		//adjust time delta
		Date now = new Date();
		long nowInMs= now.getTime();  //assume this is always postive. 	
		//this delta value reflects the sum of network latency and timer gap. It can be negative.
		long delta = (now.getHours() - update.lastDateTime.hour) * 3600000 + 
						(now.getMinutes() - update.lastDateTime.minute) * 60000 + 
						(now.getSeconds() - update.lastDateTime.second)*1000 + 
						(nowInMs%1000l - update.lastDateTime.milliseconds);

		//initialize the m_atTimeGap value
		if (m_sr.m_atTimeGap == -1){
			m_sr.m_atTimeGap = delta;
		}

		delta = delta - m_sr.m_atTimeGap; //this the delta after the adjustment
		//adjust m_atTimeGap
		m_sr.m_atTimeGap += delta/2;  //change the adjusting time gap value
		long second = (nowInMs- delta)/1000l;
		
		
		if(second<sd.getLastSecond()){
		//delayed tick
			for(String client:sd.getClients()){
				StreamerRun.Client c = m_sr.m_clientMgr.get(client);
				if(c!=null){
					if(c.lastSecond > second + 1){
						if(c.delayedTicks.length() !=0){
							c.delayedTicks +=";";
						}
						c.delayedTicks += m_sr.second2ts(second);
						c.delayedTicks += "-";
						c.delayedTicks += String.format("%.2f", price); 
						c.delayedTicks += "-";
						c.delayedTicks += String.valueOf(vol); 
					}
				}
			}			 
		}
		sd.update(second, vol, price, 0);
	 	long duration = System.currentTimeMillis()-start;
		System.out.println(symbol + ":" + String.valueOf(second)+ "," + String.valueOf(price) + "," + String.valueOf(vol)+","+String.valueOf(duration));
	}	
}

