import java.io.File;
import java.io.IOException;
import java.net.Socket;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.Helpers;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATSYMBOL;
import at.shared.ATServerAPIDefines.ATGUID;
import at.shared.ATServerAPIDefines.SYSTEMTIME;
import org.json.JSONException;
import org.json.JSONObject;


public class ATTickDataFetcher {
    private static Socket socket;
    private static ActiveTickServerAPI serverapi;
    private static APISession apiSession;
    private static boolean CANCEL = false;
    private static final Logger logger = Logger.getLogger(ATTickDataFetcher.class.getName());
    private static final int MIN_INTERVAL = 60;  //minimum allowed time window
    private static final String DEFAULT_BEGIN_TIME = "093000"; //default query start time
    private static final int DEFAULT_TIME_WINDOW = 18000; //this indicates the overall length of time in sec the client is trying to get data from
    private static final String DEFAULT_OUTPUT_DEST = "/home/kaiwen/workspace/savant-torrey-ranch/src/chihuahua/fetcher/data";
    public Stack<JSONObject> pendingRequests;
    public String beginTime;
    public int timeWindow;

    public ATTickDataFetcher() {
        serverapi = new ActiveTickServerAPI();
        apiSession = new APISession(serverapi,this);
        serverapi.ATInitAPI();
        this.pendingRequests = new Stack<JSONObject>();
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
                String strBeginDateTime = date + this.beginTime;
                try {
                    String strEndDateTime = date + addTime(this.beginTime,this.timeWindow);
                    this.setRequestOutputPath(symbol,date);
                    long res = this.sendATRequest(symbol,strBeginDateTime,strEndDateTime);
                    if (res < 0) {
                        logger.log(Level.INFO,"Error in request");
                        errcode = "-1";
                        errmsg = "Error in request";
                    } else {
                        request.put("beginDateTime",strBeginDateTime);
                        request.put("endDateTime",strEndDateTime);
                        this.addPendingRequest(request);
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
                this.addPendingRequest(buildRequest(symbol, date, midPointDateTime, endDateTime));
                //logger.log(Level.INFO,"First half: " + beginDateTime + " --- " + midPointDateTime);
                this.addPendingRequest(buildRequest(symbol, date, beginDateTime, midPointDateTime));
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
                logger.log(Level.INFO, "request complete");
                this.reset();
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

    public JSONObject buildRequest (String symbol,String date,String beginDateTime,String endDateTime) throws JSONException {
        JSONObject request = new JSONObject();
        request.put("symbol",symbol);
        request.put("date",date);
        request.put("beginDateTime",beginDateTime);
        request.put("endDateTime",endDateTime);
        return request;
    }

    public void sendNextRequest() throws JSONException {
        JSONObject nextRequest = this.getPendingRequest();
        String symbol = (String)nextRequest.get("symbol");
        String beginDateTime = (String)nextRequest.get("beginDateTime");
        String endDateTime = (String)nextRequest.get("endDateTime");
        this.sendATRequest(symbol,beginDateTime,endDateTime);
    }

    public boolean isIdle() {
        return this.pendingRequests.empty();
    }

    private void addPendingRequest(JSONObject request) {
        this.pendingRequests.push(request);
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

    private void reset() {
        this.beginTime = DEFAULT_BEGIN_TIME;
        this.setTimeWindow(DEFAULT_TIME_WINDOW);
        CANCEL = false;
    }

    private void setRequestOutputPath(String symbol,String date) {
        String outputPath = DEFAULT_OUTPUT_DEST + "/" + symbol + "_" + date + ".txt";
        File data = new File(outputPath);
        if (data.exists()) {
            data.delete();
        }
        try {
            data.createNewFile();
        } catch (IOException e) {
            logger.log(Level.SEVERE,"Request halted: cannot create file");
        }
        apiSession.GetRequestor().setOutputPath(outputPath);
    }

    private void cancelRequest() {
        this.pendingRequests.clear();
    }

    private void exit() {
        apiSession.UnInit();
        serverapi.ATShutdownAPI();
    }
}
