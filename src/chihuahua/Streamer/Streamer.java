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

public class Streamer 
{
    private static Socket socket;
    private ExecutorService exService;
    private final int POOL_SIZE = 10;
	private HashMap<String, ArrayList<ArrayList<Double>>> map;
    private ServerSocket serverSocket;

    String host = "192.168.1.121";
    //String host = "localhost";
    int port = 8091;
    int i = 0;    
    int totalNum = 0;

    public static void main(String[] args) throws IOException 
    {
            new Streamer().acceptClient();
    }
         
    public Streamer() throws IOException{
		
            InetAddress bindAdd = InetAddress.getByName(host);
            
            serverSocket = new ServerSocket(port, 100, bindAdd);
            
            totalNum = Runtime.getRuntime().availableProcessors()*POOL_SIZE;
        
            exService = Executors.newFixedThreadPool(totalNum);        
       
            map = JavaToJson.readMap();

            System.out.println("Server Started and listening to the port 8091");
    }

    public void acceptClient()
    {    
        while (true){
            Socket socket = null;
            try{
                socket = serverSocket.accept();
                System.out.println("ready for next client");
                
                exService.execute(new Handler(socket, map));
            
            } catch (Exception e){
                e.printStackTrace();
            } 		
        }       
    }

class Handler implements Runnable{
	
	private Socket socket;
	private HashMap<String, ArrayList<ArrayList<Double>>> map;
	
	public Handler(Socket socket,  HashMap<String, ArrayList<ArrayList<Double>>> map){
		this.socket = socket;
		this.map = map;
	
	}
	
	public void run() {
            
        ArrayList<ArrayList<Double>> lRet = new ArrayList<ArrayList<Double>>();
        ArrayList<Double> rData = new ArrayList<Double>();
 
        try{

            System.out.println("Socket accepted");
                
            while(true){   
                
                InputStream is = socket.getInputStream();
                
                if (is.available() != 0 ){
                    
                    InputStreamReader isr = new InputStreamReader(is);
                    
                    BufferedReader br1 = new BufferedReader(isr);
                    
                    String jstr = br1.readLine();
                    
                    System.out.println("Message received from client is "+jstr);
                    
                    String returnMessage =  null;
                        
                        JSONObject obj = new JSONObject(jstr);
                        JSONObject req  = obj.getJSONObject("request");
                        
                        String cmd = req.getString("command");
                        String cl = req.getString("client");
                    //    String sList = req.getString("symlist").toLowerCase();
                        JSONArray sList = (JSONArray)req.get("symlist");
		//	int i = 0;
                        if(cmd.equals("subscribe")){
                                        
                            if (sList.length() == 0){
                                
                                break;
                            
                            }else{
				
				Iterator<String> itr = sList.iterator();
				while(itr.hasNext())
				{	
					//itr = itr + "_quote";

					System.out.println("sList is " + itr); 
				
				        if (!map.containsKey(itr)){
                                
                                        String fname = itr +"_quote.txt"; 
                                        System.out.println("add a new list : "+ itr);
                                
                                       map.put(itr, JavaToJson.readData(fname.toLowerCase()));
                                       returnMessage = "Added the new list\n"; 
                              
				        }else{
				     
					System.out.println( sList + "is subscribed");
					lRet = map.get(itr);
					
					System.out.println("map contains list : "+ itr);
				       
					
					returnMessage = "exist\n"; 
				     
				     }
				}
			}
                        }else if(cmd.equals("update")){
                              //lRet = map.get(sList);
                                System.out.println("map contains list : "+ sList);
                               //Iterator<ArrayList<Double>> it = lRet.iterator();
				
			//	if (it.hasNext()){
				   while(i < 3600){
					rData = lRet.get(i);
					i++;
                                System.out.println("i is  : "+ i);
				  }

			//	}
                                returnMessage = rData + "\n";
                                //returnMessage = "Command is invalid\n"; 
                       
                        }else{
                            returnMessage = "No Sym\n";
                        }
                   
                    //Sending the response back to the client.
                    OutputStream os = socket.getOutputStream();
                    OutputStreamWriter osw = new OutputStreamWriter(os);
                    //PrintWriter pw = new PrintWriter(os);
            BufferedWriter bw = new BufferedWriter(osw);
            //System.out.println(returnMessage);
                    bw.write(returnMessage);
            //pw.println(returnMessage);
                    System.out.println("Message sent to the client is "+returnMessage);
                    bw.flush();
            //pw.flush();
                    //socket.close();
            System.out.println("closed");
            System.out.println(returnMessage);
                }
            
        }
            }catch(FileNotFoundException ex){
                    System.out.println("errorMessage:" + ex.getMessage());
            }catch(IOException ix){
                    System.out.println("IOException" +  ix.getMessage());
            }catch (Exception e) 
            {
                e.printStackTrace();
            }
            finally
            {
                try
                {
                    socket.close();
            System.out.println("Socket CLosed");
                }
                catch(Exception e){}
            }
        }

    }

/*
    public static void readMap(String dir, HashMap<String, ArrayList<ArrayList<Double>>> map)
    {    
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
     }
                   
                   
public static ArrayList<ArrayList<Double>> readData(String frn)
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

    if(map.containsKey("qqq_trade")){
	    ArrayList<ArrayList<Double>> arr = map.get("qqq_trade");
	    for (ArrayList<Double> d: arr)
	    {
		    System.out.println("each is " + d);
	    }

    }*/
/*	    br.close();
    
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

*/

}
