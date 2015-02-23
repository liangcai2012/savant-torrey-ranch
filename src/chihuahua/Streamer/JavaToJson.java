import java.io.BufferedReader;
import java.io.BufferedWriter;
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
 

import org.json.*;

//import Data;

/*
 * Read Tick Data
 *
 *
 *
 */


public class JavaToJson 
{
 
          // private String dir = "/Users/jingjingpeng/savant-torrey-ranch/src/chihuahua/data";

          // private static  HashMap<String, ArrayList<ArrayList<Double>>> map;
           //= new HashMap<String, ArrayList<ArrayList<Double>>>();
            
           private  ArrayList<ArrayList<Double>> lRet;
   
   
   // public static HashMap<String, ArrayList<ArrayList<Double>>> readMap(String dir, HashMap<String, ArrayList<ArrayList<Double>>> map)
     public static  HashMap<String, ArrayList<ArrayList<Double>>> readMap() throws IOException
    {    
         String dir = "/Users/jingjingpeng/savant-torrey-ranch/src/chihuahua/data";
         
	 HashMap<String, ArrayList<ArrayList<Double>>> map = new HashMap<String, ArrayList<ArrayList<Double>>>();
            
        
        try{
                File folder = new File(dir);

                File[] listOfFiles = folder.listFiles();

                for(File file : listOfFiles){
                    
                    if(file.isFile()){
                            
                            String fn = file.getName();
                            String frn = dir + "/"+fn;
                           
                            fn = fn.substring(0, fn.indexOf('.'));
                            map.put(fn, readData(frn));
                             
                      }
                 }
                   
	}catch (Exception e) 
	{
	    e.printStackTrace();
	}

	return map;
     }
                   
                   
public static  ArrayList<ArrayList<Double>> readData(String frn)
{
	
	String line;

	ArrayList<ArrayList<Double>> all = new ArrayList<ArrayList<Double>>();

	String t0 = "9:30:0]";
	double n = 0;
	double price = 0;
	double amount = 0;
	double iPri = 0;
	double iAmt = 0;

    try{
	
	BufferedReader br = new BufferedReader(new FileReader(frn));
	
	while((line = br.readLine()) != null)
	{
	    String[] ret = line.split(" ");

	    String[] prc = ret[6].split(":");
	    iPri = Double.parseDouble(prc[1]);

	    String[] amt = ret[8].split(":");
	    iAmt = Double.parseDouble(amt[1]);

	    ArrayList<Double> each = new ArrayList<Double>();

	    if(!ret[2].equals(t0))
	    {
		each.add(n);
		each.add(price/amount);
		each.add(amount);
		all.add(each);

		t0 = ret[2];
		amount = iAmt;
		n++;

	    }else{
		price = price + iPri*iAmt;
		amount = amount + iAmt;
	    }
	}

	ArrayList<Double> last = new ArrayList<Double>();
	
	last.add(n);
	last.add(price/amount);
	last.add(amount);
	all.add(last);
	
/*for (ArrayList<Double> d: all)
    {
	    System.out.println("each is " + d);
    }

 /*   if(map.containsKey("qqq_trade")){
	    ArrayList<ArrayList<Double>> arr = map.get("qqq_trade");
	    for (ArrayList<Double> d: arr)
	    {
		    System.out.println("each is " + d);
	    }

    }*/
	    br.close();
    
    }catch(FileNotFoundException ex){
	    System.out.println("errorMessage:" + ex.getMessage());
    }catch(IOException ix){
	    System.out.println("IOException");
    }catch (Exception e) 
    {
	e.printStackTrace();
    }
 
		   return all;
 }



}
