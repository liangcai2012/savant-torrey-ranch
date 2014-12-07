import java.io.*;
import java.net.*;

import org.json.JSONArray;
import org.json.JSONObject;  
import java.util.HashMap;  
import java.util.Map; 
import java.util.concurrent.*;  




 
class JavaServer {
	
		private int port=8080;
	    private ServerSocket serverSocket;
	    private ExecutorService executorService;
	    private final int POOL_SIZE=10;
	    private JSONArray StockDataJson; 
	    
	    public static void main(String[] args) throws IOException {		
	    	new JavaServer().service();		 
	    }

	    public JavaServer() throws IOException{
	    	
	    	StockDataJson= CSVtoJson.getdata(); // get all historical data
	    	
	    	serverSocket=new ServerSocket(port);
	        
	        int totThreadNum=Runtime.getRuntime().availableProcessors()*POOL_SIZE;
	        executorService=Executors.newFixedThreadPool(totThreadNum);
	        System.out.println("total thread number: "+ totThreadNum);
	        System.out.println("server start");
	        
	        
;
//	        System.out.println(CSVtoJson.getdata()); // don't uncomment, it's really slow to show
	    }
	    
	
	    
	    public void service(){
	    	
	    	while(true){
	            Socket client=null;
	            try {
	            
	            	client=serverSocket.accept();
	                executorService.execute(new Handler(client,StockDataJson));

	            } catch (Exception e) {
	                e.printStackTrace();
	            }
	        }
	    }
        
	    
	    class Handler implements Runnable{
	    	private Socket client;
	    	private JSONArray data;
	    	public Handler(Socket client,JSONArray data){
	            this.client=client;
	            this.data= data;
	        }
	    	
	    	public void run() {
	    		
	    		// old hard-coded data //
//	   		 	Map<String, String> map1 = new HashMap<String, String>();  
//	            map1.put("name","AAPL");  
//	            map1.put("price","120");  
//	            map1.put("op","buy");  
//	            JSONObject json1 = new JSONObject(map1); 
//	            String jsonString1 = "";  
//	            jsonString1 = json1.toString();   
//	            
//	            Map<String, String> map2 = new HashMap<String, String>();  
//	            map2.put("name","FB");  
//	            map2.put("price","90");  
//	            map2.put("op","buy");  
//	            JSONObject json2 = new JSONObject(map2); 
//	            String jsonString2 = "";  
//	            jsonString2 = json2.toString();
	       
	            
              	BufferedReader in = null;  
                PrintWriter out = null;  
                      
                 try {  
                          
                	 in = new BufferedReader(new InputStreamReader(client.getInputStream()));  
                     out = new PrintWriter(client.getOutputStream());  
       
                     String msg = in.readLine();  
//                     if (msg.contains("FB")){
                            	  out.println(data);  
                            	  out.flush();  
//                            	  System.out.println("send to client:" +data);
//                            	  }
                     
                              
                 } catch(IOException ex) {  
                          ex.printStackTrace();  
                 } finally {  
                          try {  
                              in.close();  
                          } catch (Exception e) {}  
                          try {  
                              out.close();  
                          } catch (Exception e) {}  
                          try {  
                              client.close();  
                          } catch (Exception e) {}  
                  } 
               }
                    
          }  
      } 
        	  
