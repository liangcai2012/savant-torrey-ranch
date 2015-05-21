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
            ServerSocket serverSocket = new ServerSocket(port);
            while (true) {
                Socket socket = serverSocket.accept();
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String strRequest = in.readLine();
                System.out.println("Request received: " + strRequest);
                JSONObject jsonRequest = new JSONObject(strRequest);
                Map response = fetcher.processRequest(jsonRequest);
                BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                JSONObject jsonResponse = new JSONObject();
                for (Object key : response.keySet()) {
                    jsonResponse.put((String)key,response.get(key));
                }
                out.write(jsonResponse.toString());
                socket.close();
            }
        }
        catch (IOException ix) {
            System.out.println(ix.getMessage());
        }
        catch (Exception e) {
            System.out.print(e.getMessage());
        }
    }
}
