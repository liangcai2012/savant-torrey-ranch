import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.*;
import java.lang.*;
import java.net.ServerSocket;
import java.net.Socket;

/**
* A simple socket server
*
*/
public class Streamer {
    
    private ServerSocket serverSocket;
    private int port;
    
    public Streamer(int port) {
        this.port = port;
    }
    
    public void start() throws IOException {
        System.out.println("Starting the socket server at port:" + port);
        serverSocket = new ServerSocket(port);
        
        //Listen for clients. Block till one connects
        
        System.out.println("Waiting for clients...");
        Socket client = serverSocket.accept();
        
        //A client has connected to this server. Send welcome message
        sendWelcomeMessage(client);
    }
    
    private void sendWelcomeMessage(Socket client) throws IOException {
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(client.getOutputStream()));
        String str;

	BufferedReader br = new BufferedReader(new FileReader("qqq_quote.txt"));
	try{
		StringBuilder sb = new StringBuilder();
		String line = br.readLine();

		while(line != null){
			sb.append(line);
		//	sb.append(System.lineSeparator());
			line = br.readLine();
		}
		str = sb.toString();
	}finally {
		br.close();
	}
	
	writer.write(str);
        writer.flush();
        writer.close();
    }
    
    /**
    * Creates a SocketServer object and starts the server.
    *
    * @param args
    */
    public static void main(String[] args) {
        // Setting a default port number.
        int portNumber = 9990;
        
        try {
            // initializing the Socket Server
            Streamer streamer = new Streamer(portNumber);
            streamer.start();
            
            } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
