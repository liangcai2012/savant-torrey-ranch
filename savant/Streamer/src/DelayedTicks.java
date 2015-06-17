import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;


//data structure to store delayed ticks for each subscribed symbol
// delayed ticks are ticks with delay more than 1 sec. These tick data is sent in the response to the next bar request (note it is only for bar data request, moving average data request does not get delayed ticks) 

//The data structure is a table of timestamps (last second of bar data), interval (bar data width) and delayed data list. 
//  timestamp |  interval  |  delays

// We assume that bar data request is sent with the same interval as the bar data width (eg. once a minute for a one-min bar) so we use timestamp(the last second of the bar data) and interval as a signature of all bar requests. Note that there can be two requests having exactly same timestamp and interval, we will have two entries for that.

//algo:
//On a bar request, 
// 1.append the new request to the table, 
// 2.go through the table and remove all entries where ct (current time) - timestamp > interval or (ct-timestamp > max delayed time and delays is empty) 
// 3. if there is entry where ct - timestamp == interval and delays is not empty, we return this delay,  remove this entry and quit.

//on a delayed tick received
// add it to all entries. 


//05/06:
	
//send this delay data to who? send related interval
//per symbol datastructure

public class DelayedTicks{

	//these arraylistes should be of same length
	private ArrayList<Long> timestamps;
	private ArrayList<Integer> intervals;
	//private ArrayList<ArrayList<String>> delays;
	private Queue<SymData> delays;  // maybe use Queue instead
	
	public DelayedTicks(){
		timestamps = new ArrayList<Long>();
		intervals= new ArrayList<Integer>();
		//delays = new ArrayList<ArrayList<String>>();
		delays = new LinkedList<SymData>();
	}

//check if there is a delay
//if Yes, add last data as current one
//quan ju de biao 
	//fanhui wanle shandiao 
	//public void onDelayedTick(long second, long vol, long price){
	public void onDelayedTick(long preTime, long curTime, long vol, double price){
	synchronized(this){ 
		System.out.println("ondt");
		long timeGap = curTime - preTime;
		long dTime = preTime;
		SymData lSd = new SymData();
		
		
		if(timeGap > 1 || timeGap < 0){
			System.out.println("timeGap is" + timeGap);
			timeGap = Math.abs(timeGap);
			
			
			while((timeGap-1) != 0){
				
				lSd.update(dTime+1, vol, price, 0);
				System.out.println("symData updated");
				delays.add(lSd);
				timestamps.add(dTime+1);
				dTime ++;
				timeGap--;
				
			}
		}else{
			System.out.println("No Delay");
		}
		
			
			
		}
	}
//? the same as getBar
//generat append string
//
//every time when the streamer got request
//check onBarRequest to see if there is any data
//if has, then return 
	public SymData onBarRequest(long second){
		synchronized(this){ 
			SymData ret = new SymData();
			if(!delays.isEmpty() && timestamps.get((int) second) != null){
				
				ret = delays.remove();
				timestamps.remove(second);
			
			}
			return ret;
		}
	}
	
}
