import com.thetransactioncompany.jsonrpc2.*;
import com.thetransactioncompany.jsonrpc2.server.*;
import java.util.*;
import java.net.*;
import java.io.*;

public class RPCHandler {
	
	//Implements a handler for a getTickData method
	public static class TickDataHandler implements RequestHandler {
		// Initialize simple tick data
		private static Map<String,Integer> tick_data = new HashMap<String,Integer>();
		static {
			tick_data.put(new String("AAPL"),100);
			tick_data.put(new String("GOOG"),500);
		}
		
		// Reports the method names of the handled requests
		public String[] handledRequests() {
			return new String[]{"getTickData"};
		}
		
		// Processes the requests
		public JSONRPC2Response process(JSONRPC2Request req, MessageContext ctx) {
			if (req.getMethod().equals("getTickData")) {
				List params = (List)req.getParams();
				String symbol = (String)params.get(0);
				if (tick_data.containsKey(symbol)) {
					return new JSONRPC2Response(tick_data.get(symbol),req.getID());
				}
				else {
					return new JSONRPC2Response("NULL",req.getID());
				}
			}
			else {
				return new JSONRPC2Response(JSONRPC2Error.METHOD_NOT_FOUND,req.getID());
			}
		}
	}
	
	public static void main (String[] args) {
		// Create a new JSON-RPC 2.0 request dispatcher
		Dispatcher dispatcher = new Dispatcher();
		
		// Register the "getTickData" handlers with it
		dispatcher.register(new TickDataHandler());
		
		// Obtain RPC request from client
		int port_num = 8080;
		
		try (
			ServerSocket server_socket = new ServerSocket(port_num);
			Socket client_socket = server_socket.accept();
			PrintWriter out = new PrintWriter(client_socket.getOutputStream());
			BufferedReader in = new BufferedReader(new InputStreamReader(client_socket.getInputStream()));
		) {
			String input = in.readLine();
			JSONRPC2Request req = JSONRPC2Request.parse(input);
			System.out.println("Request: \n" + req);
			
			JSONRPC2Response resp = dispatcher.process(req,null);
			System.out.println("Response: \n" + resp);
			out.println(resp.toString());
		} catch (UnknownHostException e) {
			System.out.println(e.getMessage());
		} catch (IOException e) {
			System.out.println(e.getMessage());
		} catch (JSONRPC2ParseException e) {
			System.out.println(e.getMessage());
		}
	}
}
