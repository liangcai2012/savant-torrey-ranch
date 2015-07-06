import java.util.Arrays;
import java.util.HashSet;
import java.lang.Math;

//data structure for each subscribed symbol
//it maintains a window of volume and Price*Vol to provide moving average
//of different intervals. Based on need, we update the moving average for
//certain intervals anytime we receive new data or update request from client
//
//Open, Close, high, low data have be calculated based on need. And it is not usual for a client
//to ask for moving open/close/high/low data. 
//

//pos always points to the last updated data
//The data returned in get function is 1 second in delay to allow delayed AT data
//Eg:
//t= 1   2   3   4   5   6   7   8 
//                     pos
//when pos is 6, we assume data at t=5 is not complete, so the latest data we return is t=4 Therefore, to provide 3600s moving average, the window size  needs to be 3602  


public class SymData {
	public static String[] allowedIntervalText = {"1s", "5s", "10s", "30s", "1m", "5m", "10m", "30m", "1h"};
	public static int[] allowedInterval = {1, 5, 10, 30, 60, 300, 600, 1800, 3600};
	public static double MAXPRICE = 10000000000.0;
	
	private HashSet<String> clientSet; 
	private int pos; //the postion of slot currently getting data
	private long lastSecond;  //lastSecond in the form of System.CurrentTimeMillisecond()/1000 
	private long lastTickSecond;  //this means the last second that an actual tick is received. After update (type=0) lastTickSecond == lastSecond; after update(type=1), lastTickSecond <= lastSecond  
	private int totalSeconds;

	private double[] bw_o; //open price of each second
	private double[] bw_h; //high of each second
	private double[] bw_l; //low of each second
	private double[] bw_c; //close of each second
	private long[] bw_v; //total volume in each second

	//these are only initialized when clients request moving average or bar average
	private double[] bw_tp; //total captical (sum(p*v)) in each second

	private long[] ms_v; //total volume in each bar
	private double[] ms_tp; //total captical (sum(p*v)) in each bar

	private boolean aveEnabled;
	private boolean maEnabled[];
	private int totalAveSeconds; //total seconds since last time aveEnable was true and bw_tp was calcuated
	private int totalMaSeconds[];//total seconds for for each moving average since last time it is enabled
	
	private int intnum;
	private int winsize;

			
	public SymData(){
		intnum = allowedInterval.length;
		//to calculate the moving average of 3600, we need array of 3601 
		winsize = allowedInterval[intnum-1]+1;
		
		bw_o = new double[winsize];
		bw_h = new double[winsize];
		bw_c = new double[winsize];
		bw_l = new double[winsize];
		bw_v = new long[winsize];
		bw_tp = new double[winsize];
		//the first element of ms_v, ms_tp, maEnabled and totalMaSeconds are useless, we use bw_v, bw_tp, aveEnabled and totalMaSeconds[0] instead 
		ms_v = new long[intnum]; 
		ms_tp = new double[intnum];
		maEnabled = new boolean[intnum];
		totalMaSeconds = new int[intnum];

		Arrays.fill(bw_o, -1.0);
		Arrays.fill(bw_h, -1.0);
		Arrays.fill(bw_l, MAXPRICE);
		Arrays.fill(bw_c, -1.0);
		Arrays.fill(bw_v, 0);
		Arrays.fill(maEnabled, false);
		Arrays.fill(totalMaSeconds, -1);


		pos = 0;
		lastSecond = 0;
		lastTickSecond = 0;
		totalSeconds = 0;
		totalAveSeconds = -1;
		aveEnabled = false;
	}


	public void changeMA(int maMask){
		if (maMask == 0){
			if(!aveEnabled) 
				return;
			bw_tp = null;
			aveEnabled = false;
			totalAveSeconds = -1;
		}
		else{
			if(!aveEnabled){
				aveEnabled = true;
				totalAveSeconds = 0;
			}
		}
		int hmask = 1 << (intnum -1);
		for (int i =0; 1<<(i+1) <= hmask; i++){ 
				if ((maMask & (1<<(i+1)))== 0){
					ms_v[i] = -1;
					ms_tp[i] = -1;
					maEnabled[i] = false;
					totalMaSeconds[i] = -1;
				}
				else{
					maEnabled[i]=true;
					if(totalMaSeconds[i]==-1)
						totalMaSeconds[i] = 0;
				}
		}			
	}

//no data received from lastSecond +1 to endSecond inclusively
//Called every time when an update command is received
//Or if an tick data is received with time skip > 0 
	public void skipTill(long endSecond){
		synchronized(this){ 
			int skip, uskip;
			skip = (int) (endSecond - lastSecond);
			if(skip <=0)
				return;

			//update the moving averages first
			if(aveEnabled){
				for (int i=1; i<intnum; i++){
					if (!maEnabled[i])
						continue;
					//if skip is too big, then existing moving average is not relevant
					if (skip>allowedInterval[i]){
						ms_v[i]=0;
						ms_tp[i]=0.0;
					}
					//Deduct the values leaving the window. Since values at pos and pos-1 were not counted in the previous moving average, we need to add them first.
					else{ 
						ms_v[i]+=bw_v[pos];
						ms_tp[i]+=bw_tp[pos];
						////ms_v[i]+=bw_v[pos-1];
						////ms_tp[i]+=bw_tp[pos-1];
	
						for(int j=0; j<skip; j++){
							////tv[i] -= wv[(pos-1-allowedInterval[i]+j)%winsize];
							////tp[i] -= wp[(pos-1-allowedInterval[i]+j)%winsize];
							ms_v[i] -= bw_v[(pos-allowedInterval[i]+j)%winsize];
							ms_tp[i] -= bw_tp[(pos-allowedInterval[i]+j)%winsize];
						}
					}
					totalMaSeconds[i]+=skip;
				}
				totalAveSeconds +=skip;
			}
			totalSeconds += skip;
			lastSecond = endSecond;

			//update o/h/l/c and v/tp if needed 
			for (int i=0; i<skip; i++){ 
				pos = (pos+1)%winsize;
				bw_o[pos]=bw_h[pos]=bw_c[pos]=-1;
				bw_l[pos]=MAXPRICE;
				bw_v[pos]=0;
				if(aveEnabled){
					bw_tp[pos]=0;
				}
			}
		}
	}

	// called everytime a tick data is received or a client request is received
	//type: 0 tick data 1: client request
	//second has to be an interger reflecting current time provided  by the caller

	public void update(long asecond, long vol, double price, int type){
		synchronized(this){ 
			System.out.print("SymDataUpdating");
			long pv = 0;  
			
			long second = asecond;
			if(type ==1)
				second = Math.max(lastSecond, asecond -1);
			else
				lastTickSecond = second;

			skipTill(second -1);
			if(lastSecond < second){//then lastSecond = second-1
				//update the moving averages first
				
				if(aveEnabled){
					for (int i=1; i<intnum; i++){ //always starting from 1, skipping int=1
						if (!maEnabled[i])
							continue;
						//Deduct the left most value leaving the window. 
						ms_v[i]+=bw_v[pos];
						ms_tp[i]+=bw_tp[pos];
						ms_v[i]-=bw_v[pos-allowedInterval[i]];
						ms_tp[i]-=bw_tp[pos-allowedInterval[i]];
						totalMaSeconds[i]+=1;
					}
					totalAveSeconds+=1;
				}
				totalSeconds +=1;
				lastSecond = second;
				//update the bar window data
				pos=(pos+1)%winsize;
				if(type == 0){
					bw_o[pos] = bw_h[pos] = bw_l[pos] = bw_c[pos] = price;
					bw_v[pos] = vol;
				}
				else{
					bw_o[pos]=bw_h[pos]=bw_c[pos]=-1;
					bw_l[pos]=MAXPRICE;
					bw_v[pos]=0;
				}
				if(aveEnabled){
					bw_tp[pos]=0.0;
					if(type ==0)
						 bw_tp[pos]= (price * vol);
				}	
			}
			// if still in the same second, we only need to update the bar window when type == 0 
			if(lastSecond == second){ 
				//only update the bar window data
				if(type == 0){
					if(bw_o[pos] == -1)
						bw_o[pos]=price;
					if (bw_h[pos] < price)
						bw_h[pos] = price;
					if(bw_l[pos] > price)
						bw_l[pos] = price;
					bw_c[pos] = price;
					bw_v[pos]+=vol;
					if(aveEnabled){
						bw_tp[pos]+=price * vol;
					}
				}
			}
			//if last second > second (type can only be 0), do same as above except we need to update moving average as well.  
			else{
				if(type == 0){
					//update old bar window
					int bpos = (int)(pos - (lastSecond - second))%winsize;
					if(bw_o[bpos] == -1)
						bw_o[bpos]=price;
					if (bw_h[bpos] < price)
						bw_h[bpos] = price;
					if(bw_l[bpos] > price)
						bw_l[bpos] = price;
					bw_c[bpos] = price;
					bw_v[bpos]+=vol;
					if(aveEnabled){
						double tp = price * vol;	
						bw_tp[bpos]=tp;
						for (int i=1; i<intnum; i++){ //always starting from 1, skipping int=1
							if (!maEnabled[i])
							continue;
							if((lastSecond -second) <= allowedInterval[i]){
								ms_v[i] += vol; 
								ms_tp[i] -= tp; 
							}
						}
					}
				}
			}//end else
		}//end sync
	}	
	
	public String getBar(long second, int interval, int bar_mask){
		
		update(second, 0, 0, 1);
		String retval = "";
		//price average
		long pave;
		
		if (interval >= intnum)
			return "";

		int ival = allowedInterval[interval];
		int sPos = (pos-ival)%winsize; 
		int epos = (pos-1)%winsize;
		double open = bw_o[(pos-ival)%winsize];
		double close = bw_c[(pos-1)%winsize];
		double high = -1;
		double low = MAXPRICE;
		long vol = 0;
		int wpos = pos-ival;
		for(int i=0; i< ival; i++){
			if(high < bw_h[wpos])
				high = bw_h[wpos];
			if(low > bw_l[wpos])
				low = bw_l[wpos];
			vol += bw_v[wpos];
			wpos++;
		}
		
		retval = String.valueOf(open)+","+String.valueOf(high)+","+String.valueOf(low)+","+String.valueOf(close)+","+String.valueOf(vol);
		return retval; 
	}

	public String getMA(int interval, int ma_mask){
		String retval = "";
		if(!aveEnabled)
			return retval; 
		
      //no need to call update function again as this function is always called after getBar()     
		//update(second, 0, 0, 1);

		if(((ma_mask & 0x1)!=0) && (interval == 0)){
			retval += String.format("%.2f", bw_tp[pos]/bw_v[pos]);
			retval += ":";
			retval += String.valueOf(bw_v[pos]);
		}
		
		for(int i=1;i<intnum; i++){
			retval += ",";
			if((i>=interval) && ((ma_mask & (0x1 << i))!=0)  && maEnabled[i]){
				retval += String.format("%.2f", ms_tp[i]/ms_v[i]);
				retval += ":";
				retval += String.valueOf(ms_v[i]);
			}
		}
	return retval;
	}

	public long getLastSecond(){
		return lastSecond;
	}
	
	public void addClient(String clientName){
		clientSet.add(clientName);
	}

	public boolean delClient(String clientName){
		return clientSet.remove(clientName);
	}

	public boolean ifNoClient(){
		return clientSet.isEmpty();
	}
	
	public HashSet<String> getClients(){
		return clientSet;
	}

	public static int getInterval(String strInt){
		int i;
		for(i=0; i< allowedInterval.length;i++){
			if(strInt.equals(allowedInterval[i]))
				break;
		}
		if(i==allowedInterval.length)
			return -1;
		return i;
	}
}
