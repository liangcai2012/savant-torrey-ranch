import java.util.*;

public class RequestListener {

    public static void main(String[] args) throws InterruptedException {
        ATTickDataFetcher fetcher = new ATTickDataFetcher();
        fetcher.init();
        Thread.sleep(2000);

        Map<String,String> request = new HashMap<String,String>();
        request.put("cmd","get");
        request.put("symbol","AAPL");
        request.put("date","20150205");
        Map response = fetcher.processRequest(request);

        /*
        String hostName = "localhost";
        int port = 8080;
        try {
            ServerSocket serverSocket = new ServerSocket(port);
            while (true) {
                socket = serverSocket.accept();
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String request = in.readLine();
                System.out.println("Request received: " + request);
                Map response = processRequest(request);
                BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
                out.write(msg);
            }
        }
        catch (IOException ix) {
            System.out.println("IOException");
        }
        catch (Exception e) {
            System.out.print("");
        }
        finally {
            try {
                socket.close();
            }
            catch (Exception e) {}
        }
        */
            //exit();
        }


}
