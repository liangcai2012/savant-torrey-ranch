import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;


//data structure to store delayed ticks for each subscribed symbol
// delayed ticks are ticks with delay more than 1 sec. These tick data is sent in the response to the next bar request. For each 

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
	private class DelayedTicksEntry{
		String client;
		int interval;
		ArrayList<String> delays;
		public DelayedTicksEntry(long ts, int i){
			timestamp = ts;
			interval = i;
			delays = new ArrayList<String>();
		}
	}
	//these arraylistes should be of same length
	private ArrayList<DelayedTicksEntry> entries;
	
	public DelayedTicks(){
		entries = new ArrayList<DelayedTicksEntry>();
	}

//check if there is a delay
//if Yes, add last data as current one
	public void onDelayedTick(String time, String strPrice, long vol){
	synchronized(this){ 
		for (DelayedTicksEntry e:entries)
			e.delays.add(time + "-" + strPrice + "-" + String.valueOf(vol));
	}

//every time when the streamer got request
//check onBarRequest to see if there is any data
//if has, then return 
	public String onBarRequest(long timestamp, int interval){
		synchronized(this){ 
			entries.add(timestamp, internal)
			for (Iterator<DelayedTicksEntry> iterator = entries.iterator(); iterator.hasNext();) {
			    DelayedTicksEntry e = iterator.next();
			    if (string.isEmpty()) {
			        // Remove the current element from the iterator and the list.
			        iterator.remove();
			    }
			}
			SymData ret = new SymData();
			if(!delays.isEmpty() && timestamps.get((int) second) != null){
				
				ret = delays.remove();
				timestamps.remove(second);
			
			}
			return ret;
		}
	}
	
}
