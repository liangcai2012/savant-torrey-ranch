import java.io.*;
import java.net.*;

import org.json.*;

import java.util.HashMap;  
import java.util.Map; 
import java.util.concurrent.*;  





 
class JavaServer {
	
		private int port=8080;
	    private ServerSocket serverSocket;
	    private ExecutorService executorService;
	    private final int POOL_SIZE=10;
	    private JSONArray StockDataJson;
	    private String buckdata; 
	    
	    public static void main(String[] args) throws IOException {		
	    	new JavaServer().service();		 
	    }

	    public JavaServer() throws IOException{
	    	



    		// old hard-coded data //
//   		 	Map<String, String> map1 = new HashMap<String, String>();  
//            map1.put("name","AAPL");  
//            map1.put("price","120");  
//            map1.put("op","buy");  
//            JSONObject json1 = new JSONObject(map1); 
//            String jsonString1 = "";  
//            jsonString1 = json1.toString();   
//            
//            Map<String, String> map2 = new HashMap<String, String>();  
//            map2.put("name","FB");  
//            map2.put("price","90");  
//            map2.put("op","buy");  
//            JSONObject json2 = new JSONObject(map2); 
//            String jsonString2 = "";  
//            jsonString2 = json2.toString();
	    	
//	    	StockDataJson= CSVtoJson.getdata(); // get all historical data
	    	int length = 1024;
	    	StringBuilder builder = new StringBuilder(length);
	    	
	    	for (int i=0; i<length; i++){
	    		builder.append((char) (ThreadLocalRandom.current().nextInt(50, 56)));
	    		
	    		}
	    	
	    	buckdata=builder.toString();
	    	buckdata = "{\"a\":" +"\"" + buckdata+"\"}";
	    	System.out.println(buckdata);
	    	System.out.println(buckdata.length());
            
	    	serverSocket=new ServerSocket(port); //show package length
	        
	    	//show how many thread is available
	        int totThreadNum=Runtime.getRuntime().availableProcessors()*POOL_SIZE;
	        executorService=Executors.newFixedThreadPool(totThreadNum);
	        System.out.println("total thread number: "+ totThreadNum);
	        System.out.println("server start");
	        
	        
;
//	        System.out.println(CSVtoJson.getdata()); // don't uncomment, it's really slow to show
	    }
	    
	
	    
	    public void service(){
//	    	Socket client=null;
	    	while(true){
	            Socket client=null;
	            try {
	            	client=serverSocket.accept();
//	                executorService.execute(new Handler(client,StockDataJson));
	                executorService.execute(new Handler(client,buckdata));
	            } catch (Exception e) {
	                e.printStackTrace();
	            }
	        }
	    }
        
	    
	    class Handler implements Runnable{
	    	private Socket client;
//	    	private JSONArray data;
	    	JSONObject json1;
	    	private String data;
//	    	public Handler(Socket client,JSONArray data){
	    	public Handler(Socket client,String data){
	            this.client=client;
	            this.data= data;
	        }
	    	
	    	public void run() {
	    		

	       
	            
              	BufferedReader in = null;  
                PrintWriter out = null;  
//                PrintStream streamOut;
              
                
                 try {  
                          
                	 in = new BufferedReader(new InputStreamReader(client.getInputStream()));  
                     out = new PrintWriter(client.getOutputStream());  
//                     streamOut = new PrintStream(client.getOutputStream(), true);
                     
                     while(true){
                     String msg = in.readLine();  
                     if (msg == null){ return; }

                     json1 = new JSONObject(buckdata);
                            	  out.println(json1);  
                            	  out.flush();  
                            	  
//                     			streamOut.println(data);
                     		
//                            	  System.out.println("send to client:" +data);
//                            	  }
                     } 
                              
                 } catch(IOException ex) {  
                          ex.printStackTrace();  
                 } catch (JSONException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} finally {  
                          try {  
                              in.close();  //keep open when test trans rate
                          } catch (Exception e) {}  
                          try {  
                              out.close();   //keep open when test trans rate  
                          } catch (Exception e) {}  
                          try {  
                              client.close();    //keep open when test trans rate
                          } catch (Exception e) {}  
                 } 
                  
               }
                    
          }  
      } 
        	  
