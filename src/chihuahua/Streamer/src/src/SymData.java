import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


//data structure for each subscribed symbol
//it maintains a window of volume and Price*Vol to provide moving average
//of different intervals. Based on need, we update the moving average for
//certain intervals anytime we receive new data or update request from client
//
//Open, Close, high, low data have be calculated based on need. And it is not usual for a client
//to ask for moving open/close/high/low data. 
//


public class SymData {
	private String[] allowedIntervalText = {"1s", "5s", "10s", "30s", "1m", "5m", "10m", "30m", "1h"};
	private int[] allowedInterval = {1, 5, 10, 30, 60, 300, 600, 1800, 3600};
	
	private ArrayList<String> registeredClient;
	private long[] wv;
	private long[] wp;
	private int pos=0;
	private long lastSecond;
	private long[] tv;
	private long[] tp;

	private boolean[] mvSwitch;
	private long totalSeconds;
	
	private int intnum;
	private int maxint;
	
			
	public SymData(){
		registeredClient = new ArrayList<String>();
		intnum = allowedInterval.length;
		maxint = allowedInterval[intnum-1];
		wv = new long[maxint];
		wp = new long[maxint];
		pos = -1;
		lastSecond = 0;
		totalSeconds = 0;
		tv = new long[intnum];
		tp = new long[intnum];
		Arrays.fill(tv,  0);
		Arrays.fill(tp, 0);
		
		mvSwitch = new boolean[intnum];
		Arrays.fill(mvSwitch,  false);
		
		
	}
	public void update(long second, long vol, long price){
		if (lastSecond > second){
			System.out.println("receiving tick with invalid timestapm:"+ String.valueOf(second)+", last second is "+String.valueOf(lastSecond));
			return;
		}
		
		long pv = price * vol;
		
		if (lastSecond == second){
			wv[pos]+=vol;
			wp[pos]+=pv;
			//TODO: update v,tp,a,o,c,h.l
			return;
		}
		
		
		long step = 1;
		if(lastSecond != 0)
			step = second - lastSecond;
		totalSeconds += step;
		lastSecond = second;
		
		//get the sum of the values to be replaced before the new values are added
		long rmtv=0;
		long rmtp=0;
		for(int i=0; i<step; i++){
			rmtv += wv[(pos+1+i)%maxint];
			rmtp += wp[(pos+1+i)%maxint];
			if(i==step-1){
				wv[(pos+1+i)%maxint]=vol;
				wp[(pos+1+i)%maxint]=pv;
			}
			else{
				wv[(pos+1+i)%maxint]=0;
				wp[(pos+1+i)%maxint]=0;
			}
		}
		pos+=step;
		
		//update the moving average value
		for(int i=0; i<intnum; i++){
			if(mvSwitch[i]){
				if(totalSeconds < allowedInterval[i])
					continue;
				if(step >= allowedInterval[i]){
					tv[i]=vol;
					tp[i]=pv;
					continue;
				}
				if (i==intnum-1){
					tv[i]+=(vol-rmtv);
					tp[i]+=(pv-rmtp);
					continue;
				}
				//calculate the moving average for i=1 to intnum-2
				long rmtvi = 0;
				long rmtpi = 0;
				for (int j=0; j<step; j++){
					rmtvi+=wv[(pos- allowedInterval[i] -j)%maxint];
					rmtpi+=wp[(pos- allowedInterval[i] -j)%maxint];
				}
				tv[i]+=(vol-rmtvi);
				tp[i]+=(pv-rmtpi);
			}
		}
	}
	
	public String get(String mask, String interval){
		return "";
	}
	
	public boolean hasClient(String client){
		if (registeredClient.contains(client))
			return true;
		return false;
	}

	public void addClient(String client){
		if (! registeredClient.contains(client))
			registeredClient.add(client);
	}
	
	public void setMASwtich(List<String> intervals){
		for(String intv : intervals){
			for (int i=0; i<allowedIntervalText.length; i++){
				if (intv.equalsIgnoreCase(allowedIntervalText[i])){
					mvSwitch[i]=true;
					//since we have never calculated: update tv[i], tp[i]
					
					break;
				}
			}
		}
	}
}
