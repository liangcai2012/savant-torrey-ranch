//package Streamer;

//import JavaToJson;
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
 

//import org.json.*;
import org.json.simple.*;


public class Streamer 
{
    private static Socket socket;
    private ExecutorService exService;
    private final int POOL_SIZE = 10;
	private HashMap<String, ArrayList<ArrayList<Double>>> map;
    private ServerSocket serverSocket;

    //String host = "192.168.1.121";
    String host = "localhost";
    int port = 8091;
    int i = 0;    
    int totalNum = 0;
	
int count = 0;    
    JavaToJson js = new JavaToJson();

    public static void main(String[] args) throws IOException 
    {
            new Streamer().acceptClient();
    }
         
    public Streamer() throws IOException{
		
            InetAddress bindAdd = InetAddress.getByName(host);
            
            serverSocket = new ServerSocket(port, 100, bindAdd);
            
            totalNum = Runtime.getRuntime().availableProcessors()*POOL_SIZE;
        
            exService = Executors.newFixedThreadPool(totalNum);        
       
            map = js.readMap();

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
                    
                    String returnMessage =  "hi";
                   
                    Object oObj=JSONValue.parse(jstr);
                        
                       // JSONObject obj = new JSONObject(jstr);
                        JSONObject obj = (JSONObject) oObj;
                        //JSONObject req  = obj.getJSONObject("request");
                        JSONObject req  = (JSONObject)obj.get("request");
                        
                        String cmd = (String)req.get("command");
                        String cl = (String)req.get("client");
                    //    String sList = req.getString("symlist").toLowerCase();
                        JSONArray sList = (JSONArray)req.get("symlist");
		//	int i = 0;
			Iterator<String> iterator = sList.iterator();
                        if(cmd.equals("subscribe")){
                                        
                           // if (sList.length() == 0){
                                
                             //   break;
                            
                           // }else

			
                            	//for(int i = 0; i < sList.length(); i++){
                                while(iterator.hasNext()){  
				   // Iterator<String> iterator = sList.iterator();
				//	JSONObject jsArr = (JSONObject)sList.getJSONObject(i);
                                  //    String[] syms = JSONObject.getNames(jsArr);
                                    //  for(String sym : syms){
		                        String sym = iterator.next();
					System.out.println("current load is " + sym); 
	                                 sym = sym.toLowerCase();			
				        if (!map.containsKey(sym)){
                                
                                        String fname = sym +"_trade.txt"; 
                                        System.out.println("add a new list : "+ sym);
                                        fname = "/home/chuan/git/savant-torrey-ranch/src/chihuahua/data/"+fname.toLowerCase();                                
                                       map.put(sym, js.readData(fname));
                                       returnMessage = "Added the new list\n"; 
                              
				        }else{
				     
					                   System.out.println( sym + "is subscribed");
					                    returnMessage = "Subscribed!!!\n"; 
					
					                    System.out.println("map contains list : "+ sym);
				       
					
				     
				          }
				      //}
                            	}
                           // }
                        }else if(cmd.equals("update")){
                        
                       		String itv = (String)req.get("interval");
                       		System.out.println(itv);
                        	itv = itv.substring(0, itv.length() - 1);
                        	int sec = Integer.parseInt(itv);
                              //lRet = map.get(sList);
                                System.out.println("map contains list : "+ sList);
				String res = "";
				
				OutputStream os = socket.getOutputStream();
                OutputStreamWriter osw = new OutputStreamWriter(os);
                BufferedWriter bw = new BufferedWriter(osw);
				
				
				while(iterator.hasNext()){
					System.out.println("ssssssssssss ");
		                        String sy = iterator.next().toLowerCase();
					     lRet = map.get(sy);
                               //Iterator<ArrayList<Double>> it = lRet.iterator();
					     System.out.println(sy);
					     System.out.println(lRet);
					     System.out.println(count);
					     
					     if (count < lRet.size()){
					     
			 			ArrayList<Double> result =  lRet.get(count);
//                               		for(int i = 0; i < result.size(); i++){
						  res = "[" + result.get(0) + "," + result.get(1) + "," + result.get(2) +"]";
						   
//					}
						  returnMessage = res + "\n";    
			}
				
                              
                                //returnMessage = "Command is invalid\n"; 
                       
//                        }
			//else{
                          //  returnMessage = "No Sym\n";
                       // }
                   
                    //Sending the response back to the client.
                    
            //System.out.println(returnMessage);
                    bw.write(returnMessage);
            //pw.println(returnMessage);
                    System.out.println("Message sent to the client is "+returnMessage);
				}
                    bw.flush();
                        
            //pw.flush();
                    //socket.close();
            System.out.println("closed");
            System.out.println(returnMessage);
                }
                        count = count + 1;
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
