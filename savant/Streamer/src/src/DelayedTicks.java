import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


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



public class DelayedTicks{

	//these arraylistes should be of same length
	private ArrayList<Integer> timestamps;
	private ArrayList<Integer> intervals;
	private ArrayList<ArrayList<String>> delays;

	public DelayedTicks(){
		timestamps = new ArrayList<Integer>();
		intervals= new ArrayList<Integer>();
		delays = new ArrayList<ArrayList<String>>();
	}


	public void onDelayedTick(long second, long vol, long price){
		synchronized(this){ 
		}
	}

	public String onBarRequest(long second, long interval){
		synchronized(this){ 
			return "";
		}
	}
	
}
