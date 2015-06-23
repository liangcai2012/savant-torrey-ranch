import java.io.*;
import java.net.Socket;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.text.DateFormat;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import java.io.FileNotFoundException;

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
    private static final SavantConfig config = SavantConfig.getConfig();
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

//    public Date time_begin,time_end;
//    public long time_diff;

    static {
        DEFAULT_OUTPUT_DEST = config.getProperty("OUTPUT_DIR") + "/data";
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
        String atHostName = config.getProperty("AT_HOSTNAME");
        int atPort = Integer.parseInt(config.getProperty("AT_PORT"));
        String guid = config.getProperty("AT_GUID");
        String userId = config.getProperty("AT_USER");
        String password = config.getProperty("AT_PASSWORD");

        ATGUID atguid = (new ATServerAPIDefines()).new ATGUID();
        atguid.SetGuid(guid);

        boolean rc = apiSession.Init(atguid, atHostName, atPort, userId, password);
        logger.info("init status: " + (rc ? "ok" : "failed"));
    }

    public Map processRequest(JSONObject request) throws JSONException, FileNotFoundException {
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
                
                //time_begin = new Date();
                                
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


    //validate the input date string. Use the solution from http://stackoverflow.com/questions/226910/how-to-sanity-check-a-date-in-java
    public boolean checkDate(String strDate) {
        if (strDate.length() != 8) {
            return false;
        } 
        //int year = Integer.parseInt(strDate.substring(0, 4));
        //int month = Integer.parseInt(strDate.substring(4, 6));
        //int day = Integer.parseInt(strDate.substring(6, 8));
        Date date = null;
        SimpleDateFormat sdf = (SimpleDateFormat)DateFormat.getDateInstance();
        sdf.applyPattern("yyyymmdd");
        sdf.setLenient(false);
        try{
            date = sdf.parse(strDate);
        }
        catch(ParseException e)
        {
            logger.log(Level.SEVERE,"You're providing an invalid date!");
              return false;
        }  
        Date today = new Date();
        //Calendar cal = Calendar.getInstance();
        //cal.set(year, month, day);
        //if (cal.after(today)) {
        if (date.after(today)){
            logger.log(Level.SEVERE,"You're trying to get data from the future!");
            return false;
        }
        return true;
  }

    public void onTickHistoryOverload() {
        JSONObject lastRequest = this.getPendingRequest();
        this.removePendingRequest();
        this.setTimeWindow(this.timeWindow / 2);
        if (this.timeWindow >= MIN_INTERVAL) {
            try {
                String symbol = (String)lastRequest.get("symbol");
                String beginDateTime = (String)lastRequest.get("beginDateTime");
                String endDateTime = (String)lastRequest.get("endDateTime");
                String date = beginDateTime.substring(0, 8);
                int deltaT = (int)subtractTime(endDateTime.substring(8),beginDateTime.substring(8));
                if (deltaT != this.timeWindow * 2) {
                    logger.log(Level.INFO,"Reset time window");
                    this.setTimeWindow(deltaT/2);
                }
                String midPointTime = addTime(this.beginTime,this.timeWindow);
                this.insertPendingRequest(buildRequest(symbol, date, midPointTime, endDateTime.substring(8)));
                this.insertPendingRequest(buildRequest(symbol, date, beginDateTime.substring(8), midPointTime));
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

    public void readLog(long[] ts,String fn) 
    {
        Reader reader = null;
        BufferedReader br = null;
        try {
			File f = new File(fn);
			if(!f.exists())
				return; 
            reader = new FileReader(fn);
            br = new BufferedReader(reader);
            
            String data = null;
            int cnt=0;
            while (cnt<1 && (data = br.readLine()) != null) {
                  ts[cnt++]=Long.parseLong(data);    
            }
        } 
        catch (IOException e) {
            //e.printStackTrace();
        } 
        finally {
            try {
                reader.close();
                br.close();
            } 
            catch (Exception e) {
               // e.printStackTrace();
            }
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
                long totalLength=this.completeFetch();
                this.reset();
                logger.log(Level.INFO, "request complete");
    
		//Using output.txt is not very necessary, we can use du command as replacement.             
			//This is only for dumping the total file size to the output.txt file for total size estimation. 
///*
                //SimpleDateFormat dateFormat = new SimpleDateFormat("HH:mm:ss");
                //time_end = new Date();
                try{
                    long[] ts={0,0};
                    readLog(ts,"./output.txt");

                    File writename = new File("./output.txt"); 
                    writename.createNewFile();
                    BufferedWriter out = new BufferedWriter(new FileWriter(writename));  
                
                //    time_diff=(time_end.getTime()-time_begin.getTime())/1000;
    				System.out.println(String.valueOf(ts[0]) +":"+String.valueOf(totalLength));            
                    out.write(String.valueOf(ts[0]+totalLength/1024));
                    
                    out.flush();
                    out.close();
                }
                catch(Exception e)
                {
                   // e.printStackTrace();
                }
  //*/              
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

    //return file size for estimation purpose
    private long completeFetch() {
        String filepath = this.outputPath + "_markethours.tsv";
        logger.log(Level.INFO, "output file is "+filepath);
       
        long res=0;

        if (new File(filepath+".tmp").exists()) {
            logger.log(Level.INFO, "compress "+filepath+".tmp");
        	res+=compressFile(filepath);
        }

        filepath = this.outputPath + "_premarket.tsv";
        if (new File(filepath+".tmp").exists()) {
            res+=compressFile(filepath);
        }

        filepath = this.outputPath + "_aftermarket.tsv";
        if (new File(filepath+".tmp").exists()) {
            res+=compressFile(filepath);
        }
        return res;
     }

    //return file size for estimation purpose
    private long compressFile(String filepath) {
        try {
            byte[] data = new byte[BUFFER];
            String zipFilePath = filepath + ".zip";
            filepath = filepath + ".tmp";
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
			System.out.println("file length: " + String.valueOf(new File(zipFilePath).length()));
            return new File(zipFilePath).length();
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Failed to compress data file");
            logger.log(Level.SEVERE, e.getMessage());
            return -1;
        }
    }

    private void reset() {
        this.beginTime = DEFAULT_BEGIN_TIME;
        this.setTimeWindow(DEFAULT_TIME_WINDOW);
        CANCEL = false;
    }

    private void setRequestOutputPath(String symbol,String date) throws FileNotFoundException{
		File outHome = new File(DEFAULT_OUTPUT_DEST);
		if(!outHome.exists()){
			if(!outHome.mkdir()){
				throw new FileNotFoundException("cannot create the home dir of the output data, check config file!");
			}
		}
        File outDir = new File(DEFAULT_OUTPUT_DEST + "/" + date);
        if (!outDir.exists()) {
			//this is not supposed to happen given that outHome has been checked. 
            if(!outDir.mkdir()){
				throw new FileNotFoundException("cannot create the dest dir of the output data, check config file!");
			}
        }
        this.outputPath = DEFAULT_OUTPUT_DEST + "/" + date + "/" + symbol;
        String premarketFilePath = this.outputPath + "_premarket.tsv.tmp";
        clearExisting(premarketFilePath);
        String marketFilePath = this.outputPath + "_markethours.tsv.tmp";
        clearExisting(marketFilePath);
        String aftermarketFilePath = this.outputPath + "_aftermarket.tsv.tmp";
        clearExisting(aftermarketFilePath);
        apiSession.GetRequestor().setOutputPath(premarketFilePath,marketFilePath,aftermarketFilePath);
    }

    private void clearExisting(String filepath) {
        File f = new File(filepath);
        if (f.exists()) {
            f.delete();
        }
    }

    private void cancelRequest() {
        this.pendingRequests.clear();
    }

    private void exit() {
        apiSession.UnInit();
        serverapi.ATShutdownAPI();
    }
}
