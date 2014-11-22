import java.io.*;
import java.net.*;
import org.json.JSONObject;  
import java.util.HashMap;  
import java.util.Map; 
import java.util.concurrent.*;  



 
class JavaServer {
	
		private int port=8080;
	    private ServerSocket serverSocket;
	    private ExecutorService executorService;
	    private final int POOL_SIZE=10;
	
	    public static void main(String[] args) throws IOException {		
	    	new JavaServer().service();		 
	    }

	    public JavaServer() throws IOException{
	        serverSocket=new ServerSocket(port);
	        
	        int totThreadNum=Runtime.getRuntime().availableProcessors()*POOL_SIZE;
	        executorService=Executors.newFixedThreadPool(totThreadNum);
	        System.out.println("total thread number: "+ totThreadNum);
	        System.out.println("server start");
	    }

	    public void service(){
	        
	    	
	    	while(true){
	            Socket client=null;
	            try {
	            
	            	client=serverSocket.accept();
	                executorService.execute(new Handler(client));

	            } catch (Exception e) {
	                e.printStackTrace();
	            }
	        }
	    }
         
	    class Handler implements Runnable{
	    	private Socket client;
	    	
	    	public Handler(Socket client){
	            this.client=client;
	        }
	    	
	    	public void run() {

	   		 	Map<String, String> map1 = new HashMap<String, String>();  
	            map1.put("name","AAPL");  
	            map1.put("price","120");  
	            map1.put("op","buy");  
	            JSONObject json1 = new JSONObject(map1); 
	            String jsonString1 = "";  
	            jsonString1 = json1.toString();   
	            
	            Map<String, String> map2 = new HashMap<String, String>();  
	            map2.put("name","FB");  
	            map2.put("price","90");  
	            map2.put("op","buy");  
	            JSONObject json2 = new JSONObject(map2); 
	            String jsonString2 = "";  
	            jsonString2 = json2.toString();
	   
//	    		ServerSocket server = new ServerSocket(8080);
//	    		System.out.println("wait for connection on port 8080");
              //Socket socket = server.accept();  
              
              	BufferedReader in = null;  
                PrintWriter out = null;  
                      
                 try {  
                          
                	 in = new BufferedReader(new InputStreamReader(client.getInputStream()));  
                     out = new PrintWriter(client.getOutputStream());  
       
                     String msg = in.readLine();  
                     if (msg.contains("FB")){
                            	  out.println(jsonString2);  
                            	  out.flush();  
                            	  System.out.println("send to client:" +jsonString2);
                            	  }
                     else if (msg.contains("AAPL")){
                            	  out.println(jsonString1);  
                            	  out.flush();  
                            	  System.out.println("send to client:" +jsonString1);
                            	  }
                              
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
        	  
