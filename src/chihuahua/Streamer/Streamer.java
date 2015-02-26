package Streamer;

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
                            	for(int i = 0; i < sList.length(); i++){
                                      JSONObject jsArr = sList.getJSONObject(i);
                                      String[] syms = JSONObject.getNames(jsArr);
                                      for(String sym : syms){
		
					System.out.println("current load is " + sym); 
				
				        if (!map.containsKey(sym)){
                                
                                        String fname = sym +"_quote.txt"; 
                                        System.out.println("add a new list : "+ sym);
                                
                                       map.put(sym, JavaToJson.readData(fname.toLowerCase()));
                                       returnMessage = "Added the new list\n"; 
                              
				        }else{
				     
					                   System.out.println( sym + "is subscribed");
					                   lRet = map.get(sym);
					
					                    System.out.println("map contains list : "+ sym);
				       
					
					                    returnMessage = "exist\n"; 
				     
				          }
				      }
                            	}
                            }
                        }else if(cmd.equals("update")){
                        	
                        	String itv = req.getString("interval");
                        	itv = itv.substring(0, itv.length() - 2);
                        	int sec = Integer.parseInt(itv);
                              //lRet = map.get(sList);
                                System.out.println("map contains list : "+ sList);
                               //Iterator<ArrayList<Double>> it = lRet.iterator();
				
			//	if (it.hasNext()){
                   int n = 1;
                   int price = 0;
                   int open = 0;
                   int amount = 0;
                   int close = 0;
                   Double[] res = new Double[3];
                   int[] retData = new int[3];
                   if (sec == 1) {
                	   rData = lRet.get(i); 
                	   res = rData.toArray(res);
                   }else{
                	  
				       while(n <= sec){
					     
				    	 //price += lRet.get(n);
				    	 rData = lRet.get(i+n-1);
				    	 //sData = lRet.get(1);
				    	 
					     res = rData.toArray(res);
					     
					     price += res[1];
					     
					     amount += res[2];
					     
					     n++;
                             //   System.out.println("i is  : "+ i);
				  }
				       
				       retData[0] = sec;
				       retData[1] = (int)price/(n-1);
				       retData[2] = (int)amount;
				       i = n;
    
				}
                                returnMessage = res + "\n";
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

}
