import java.io.*;
import java.net.Socket;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.Helpers;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATSYMBOL;
import at.shared.ATServerAPIDefines.ATGUID;
import at.shared.ATServerAPIDefines.SYSTEMTIME;
import org.json.JSONObject;
import org.json.JSONException;


public class ATTickDataFetcher {
    /*
    This class is used to fetch stock history data from ATTick server.
    Three files are generated for each request, one for market pre-hours quotes,
    one for regular hours quotes, and another for aftermarket quotes. The
    output files are named using the format: symbol_date_hours.tsv.
     */
    private static Socket socket;
    private static ActiveTickServerAPI serverapi;
    private static APISession apiSession;
    private static boolean CANCEL = false;
    private static final Logger logger = Logger.getLogger(ATTickDataFetcher.class.getName());
    private static final int MIN_INTERVAL = 60;  //minimum allowed time window
    private static final String DEFAULT_BEGIN_TIME = "060000"; //default query start time
    private static final String DEFAULT_END_TIME = "200000"; //default query end time
    private static final int DEFAULT_TIME_WINDOW = 3600; //this indicates the overall length of time in sec the client is trying to get data from
    private static final String DEFAULT_OUTPUT_DEST;
    private static final int BUFFER = 2048;
    public String outputPath;
    public LinkedList<JSONObject> pendingRequests;
    public String beginTime;
    public int timeWindow;

    static {
        String dataPath = "";
        String[] pathComp = Arrays.copyOfRange(new File("").getAbsolutePath().split("/"),1,5);
        for (String c : pathComp) {
            dataPath += "/" + c;
        }
        dataPath += "/savant/data";
        DEFAULT_OUTPUT_DEST = dataPath;
    }

    public ATTickDataFetcher() {
        serverapi = new ActiveTickServerAPI();
        apiSession = new APISession(serverapi,this);
        serverapi.ATInitAPI();
        this.pendingRequests = new LinkedList<JSONObject>();
        this.beginTime = DEFAULT_BEGIN_TIME;
        this.timeWindow = DEFAULT_TIME_WINDOW;
    }

    public void init() {
        String atHostName = "activetick1.activetick.com";
        int atPort = 443;
        String guid = "80af4953bb7f4dcf85523ad332161eff";
        String userId = "liangcai";
        String password = "S@^@nt932456";

        ATGUID atguid = (new ATServerAPIDefines()).new ATGUID();
        atguid.SetGuid(guid);

        boolean rc = apiSession.Init(atguid, atHostName, atPort, userId, password);
        System.out.println("init status: " + (rc ? "ok" : "failed"));
    }

    public Map processRequest(JSONObject request) throws JSONException {
        Map<String, String> response = new HashMap<String, String>();
        String cmd = (String)request.get("command");
        String errcode = "0";
        String errmsg = null;
        SENDREQUEST: {
            if (cmd.equals("quit")) {
                this.exit();
            } else if (cmd.equals("get")) {

                if (!this.isIdle()) {
                    logger.log(Level.SEVERE,"fetcher busy");
                    errcode = "-1";
                    errmsg = "busy";
                    break SENDREQUEST;
                }

                String symbol = (String)request.get("symbol");
                String date = (String)request.get("date");
                logger.log(Level.INFO,"SEND request [" + symbol + ":" + date + "]");
                if (!checkDate(date)) {
                    errcode = "-1";
                    errmsg = "Error in date (eg: yyyymmdd)";
                    break SENDREQUEST;
                }
                this.setRequestOutputPath(symbol, date);

                try {
                    String strCurrBeginTime = this.beginTime;
                    String strCurrEndTime = "";
                    do {
                        strCurrEndTime = addTime(strCurrBeginTime, this.timeWindow);
                        request = buildRequest(symbol,date,strCurrBeginTime,strCurrEndTime);
                        this.addPendingRequest(request);
                        strCurrBeginTime = addTime(strCurrBeginTime, this.timeWindow);
                    } while ((subtractTime(DEFAULT_END_TIME,strCurrEndTime) > 0));
                    long res = sendNextRequest();
                    if (res < 0) {
                        errcode = "-1";
                        errmsg = "Error in sending request";
                    }
                } catch(ParseException pe) {
                    logger.log(Level.INFO,"Error in time addition");
                    errcode = "-1";
                    errmsg = "Error in time addition";
                }
            } else if (cmd.equals("check")) {
                if (this.isIdle()) {
                    errcode = "-1";
                    errmsg = "Idle";
                } else {
                    response.put("latest",this.beginTime);
                }
            } else if (cmd.equals("cancel")) {
                if (this.isIdle()) {
                    errcode = "-1";
                    errmsg = "Nothing to cancel";
                } else {
                    CANCEL = true;
                }
            }
        }
        response.put("errcode", errcode);
        if (errmsg != null) {
            response.put("errmsg", errmsg);
        }
        return response;
    }

    public long sendATRequest(String symbol,String strBeginDateTime,String strEndDateTime) {
        ATSYMBOL atSymbol = Helpers.StringToSymbol(symbol);
        SYSTEMTIME beginDateTime = Helpers.StringToATTime(strBeginDateTime);
        SYSTEMTIME endDateTime = Helpers.StringToATTime(strEndDateTime);
        return apiSession.GetRequestor().SendATTickHistoryDbRequest(atSymbol, true, true, beginDateTime, endDateTime, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT);
    }

    public boolean checkDate(String strDate) {
        boolean cond = true;
        Date today = new Date();
        if (strDate.length() != 8) {
            cond = false;
        } else {
            try {
                int year = Integer.parseInt(strDate.substring(0, 3));
                int month = Integer.parseInt(strDate.substring(4, 5));
                int day = Integer.parseInt(strDate.substring(6, 7));
                Calendar cal = Calendar.getInstance();
                cal.set(year, month, day);
                if (cal.after(today)) {
                    logger.log(Level.SEVERE,"You're trying to get data from the future!");
                    cond = false;
                }
            } catch (NumberFormatException nfe) {
                cond = false;
            }
        }
        return cond;
    }

    public void onTickHistoryOverload() {
        JSONObject lastRequest = this.getPendingRequest();
        this.removePendingRequest();
        this.setTimeWindow(this.timeWindow / 2);
        if (this.timeWindow >= MIN_INTERVAL) {
            try {
                String symbol = (String)lastRequest.get("symbol");
                String date = (String)lastRequest.get("date");
                String beginDateTime = (String)lastRequest.get("beginDateTime");
                String endDateTime = (String)lastRequest.get("endDateTime");
                int deltaT = (int)subtractTime(endDateTime.substring(8),beginDateTime.substring(8));
                if (deltaT != this.timeWindow * 2) {
                    logger.log(Level.INFO,"Reset time window");
                    this.setTimeWindow(deltaT/2);
                }
                String midPointDateTime = date + addTime(this.beginTime,this.timeWindow);
                //logger.log(Level.INFO, "Second half: " + midPointDateTime + " --- " + endDateTime);
                this.insertPendingRequest(buildRequest(symbol, date, midPointDateTime, endDateTime));
                //logger.log(Level.INFO,"First half: " + beginDateTime + " --- " + midPointDateTime);
                this.insertPendingRequest(buildRequest(symbol, date, beginDateTime, midPointDateTime));
                System.out.println(pendingRequests);
                this.sendNextRequest();
            } catch (ParseException pe) {
                logger.log(Level.SEVERE,pe.getMessage());
            } catch (JSONException je) {
                logger.log(Level.SEVERE,je.getMessage());
            }
        } else {
            logger.log(Level.WARNING, "Fetch halted: Unexpected data volume");
        }
    }

    public void onRequestComplete() {
        logger.log(Level.INFO,"new data recorded");
        try {
            this.updateBeginTime();
            this.removePendingRequest();
            if (CANCEL) {
                this.cancelRequest();
            }
            if (!this.isIdle()) {
                this.sendNextRequest();
            } else {
                this.completeFetch();
                this.reset();
                logger.log(Level.INFO, "request complete");
            }
        } catch (JSONException e) {
            logger.log(Level.SEVERE,e.getMessage());
        }
    }

    public static String addTime (String time,int timePassed) throws ParseException {
        SimpleDateFormat df = new SimpleDateFormat("HHmmss");
        Date date = df.parse(time);
        Calendar cal = Calendar.getInstance();
        cal.setTime(date);
        cal.add(Calendar.SECOND,timePassed);
        return df.format(cal.getTime());
    }

    public static long subtractTime (String timeOne,String timeTwo) throws ParseException {
        SimpleDateFormat df = new SimpleDateFormat("HHmmss");
        Date dateOne = df.parse(timeOne);
        Date dateTwo = df.parse(timeTwo);
        long delta = dateOne.getTime() - dateTwo.getTime();
        return delta/1000;
    }

    public JSONObject buildRequest (String symbol,String date,String beginTime,String endTime) throws JSONException {
        JSONObject request = new JSONObject();
        request.put("symbol",symbol);
        request.put("beginDateTime",date+beginTime);
        request.put("endDateTime",date+endTime);
        return request;
    }

    public long sendNextRequest() throws JSONException {
        JSONObject nextRequest = this.getPendingRequest();
        String symbol = (String)nextRequest.get("symbol");
        String beginDateTime = (String)nextRequest.get("beginDateTime");
        String endDateTime = (String)nextRequest.get("endDateTime");
        return this.sendATRequest(symbol,beginDateTime,endDateTime);
    }

    public boolean isIdle() {
        return this.pendingRequests.isEmpty();
    }

    private void addPendingRequest(JSONObject request) {
        this.pendingRequests.add(request);
    }

    private void insertPendingRequest(JSONObject request) {
        this.pendingRequests.addFirst(request);
    }

    private void removePendingRequest() {
        this.pendingRequests.pop();
    }

    private JSONObject getPendingRequest() {
        return this.pendingRequests.peek();
    }

    private void updateBeginTime() throws JSONException {
        logger.log(Level.INFO,"Updating begin time");
        JSONObject latestRequest = this.getPendingRequest();
        String endDateTime = (String)latestRequest.get("endDateTime");
        this.beginTime = endDateTime.substring(8);
    }

    private void setTimeWindow(int window) {
        this.timeWindow = window;
    }

    private void completeFetch() {
        String filepath = this.outputPath + "_markethours.tsv";
        renameFile(filepath);
        compressFile(filepath);

        filepath = this.outputPath + "_premarket.tsv";
        renameFile(filepath);
        compressFile(filepath);

        filepath = this.outputPath + "_aftermarket.tsv";
        renameFile(filepath);
        compressFile(filepath);
    }

    private void renameFile(String filepath) {
        try {
            String tempFilePath = filepath + ".tmp";
            Runtime.getRuntime().exec("mv " + tempFilePath + " " + filepath);
            new File(filepath);
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Failed to rename temp file");
        }
    }

    private void compressFile(String filepath) {
        try {
            byte[] data = new byte[BUFFER];
            String zipFilePath = filepath + ".zip";
            BufferedInputStream in = new BufferedInputStream(new FileInputStream(filepath), BUFFER);
            FileOutputStream zipFile = new FileOutputStream(zipFilePath);
            ZipOutputStream out = new ZipOutputStream(new BufferedOutputStream(zipFile));
            ZipEntry entry = new ZipEntry(filepath);
            out.putNextEntry(entry);
            int count;
            while((count = in.read(data, 0, BUFFER)) != -1) {
                out.write(data, 0, count);
            }
            in.close();
            out.close();
            zipFile.close();
            new File(filepath).delete();
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Failed to compress data file");
            logger.log(Level.SEVERE, e.getMessage());
        }
    }

    private void reset() {
        this.beginTime = DEFAULT_BEGIN_TIME;
        this.setTimeWindow(DEFAULT_TIME_WINDOW);
        CANCEL = false;
    }

    private void setRequestOutputPath(String symbol,String date) {
        File outDir = new File(DEFAULT_OUTPUT_DEST + "/" + date);
        if (!outDir.exists()) {
            outDir.mkdir();
        }
        this.outputPath = DEFAULT_OUTPUT_DEST + "/" + date + "/" + symbol;
        String premarketFilePath = this.outputPath + "_premarket.tsv.tmp";
        createIfNotExist(premarketFilePath);
        String marketFilePath = this.outputPath + "_markethours.tsv.tmp";
        createIfNotExist(marketFilePath);
        String aftermarketFilePath = this.outputPath + "_aftermarket.tsv.tmp";
        createIfNotExist(aftermarketFilePath);
        apiSession.GetRequestor().setOutputPath(premarketFilePath,marketFilePath,aftermarketFilePath);
    }

    private void cancelRequest() {
        this.pendingRequests.clear();
    }

    private void createIfNotExist(String filepath) {
        File data = new File(filepath);
        if (data.exists()) {
            data.delete();
        }
        try {
            data.createNewFile();
        } catch (IOException e) {
            logger.log(Level.SEVERE,"Request halted: cannot create file");
        }
    }

    private void exit() {
        apiSession.UnInit();
        serverapi.ATShutdownAPI();
    }
}
