import org.json.JSONObject;
import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Arrays;
import java.util.Map;

public class RequestListener {

    public static void main(String[] args) throws InterruptedException {
        // Java server
        SavantConfig config = SavantConfig.getConfig();
        ATTickDataFetcher fetcher = new ATTickDataFetcher();
        fetcher.init();
        Thread.sleep(2000);

        String hostName = "localhost";
        int port = Integer.parseInt(config.getProperty("FETCHER_PORT"));
        try {
			Socket socket;
            ServerSocket serverSocket = new ServerSocket(port);
            while (true) {
                socket = serverSocket.accept();
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String strRequest = in.readLine();
                System.out.println("Request received: " + strRequest);
                JSONObject jsonRequest = new JSONObject(strRequest);
                Map response = fetcher.processRequest(jsonRequest);
                BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                JSONObject jsonResponse = new JSONObject();
                boolean hasExtra= false;
                for (Object key : response.keySet()) {
                    if (((String)key).equals("extra"))
                        hasExtra= true;
                    else
                       jsonResponse.put((String)key,response.get(key));
                }
                out.write(jsonResponse.toString());
                if(hasExtra){
                    out.write("extra:");
                    out.write((String)response.get("extra"));
                }
                out.flush();
                socket.close();
            }
        }
		//this is to prevent improper configured output dir. socket should be already opened.
        catch (FileNotFoundException e) {
            System.out.print(e.getMessage());
			System.exit(-1);
        }
        catch (IOException ix) {
            System.out.println(ix.getMessage());
			System.exit(-1);
        }
        catch (Exception e) {
            System.out.print(e.getMessage());
			System.exit(-1);
        }
    }
}
