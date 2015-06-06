/**
 * Created by kaiwen on 3/31/15.
 */
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.logging.*;

public class SavantLogger {

    public String logPath;
    private String moduleName;
    private Logger logger;
    private static final String DEFAULT_LOG_DIR;
    private static final String[] MODULES = {"fetcher","streamer","viewer"};
    private static FileHandler logHandler;
    private static SimpleFormatter formatter;
    private static final SimpleDateFormat fileDateFormat = new SimpleDateFormat("yyyyMMdd");
    private static final SimpleDateFormat logDateFormat = new SimpleDateFormat("hh:mm:ss");

    static {
        String path = "";
        String[] pathComp = Arrays.copyOfRange(new File("").getAbsolutePath().split("/"), 1, 5);
        for (String c : pathComp) {
            path += "/" + c;
        }
        path += "/savant/log";
        DEFAULT_LOG_DIR = path;
    }

    public SavantLogger (final String moduleName) throws WrongModuleException {
        if (!Arrays.asList(MODULES).contains(moduleName)) {
            throw new WrongModuleException("Unknown module " + moduleName);
        }
        this.moduleName = moduleName;
        this.logger = Logger.getLogger(moduleName);
        this.logPath = getLogPath();
        try {
            this.logHandler = new FileHandler(logPath,true);
            this.logger.addHandler(logHandler);
            this.logHandler.setFormatter(new SimpleFormatter() {
                public String format(LogRecord record) {
                    StringBuffer sb = new StringBuffer();
                    sb.append("[").append(logDateFormat.format(new Date(record.getMillis()))).append("]");
                    sb.append(" - ").append(moduleName.toUpperCase()).append(" - ");
                    sb.append(" ").append(record.getLevel()).append(" : ");
                    sb.append(formatMessage(record));
                    sb.append("\n");
                    return sb.toString();
                }
            });
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void log(Level level, String message) {
        if (level.equals(Level.SEVERE)) {
            logger.severe(message);
        } else if (level.equals(Level.INFO)) {
            logger.info(message);
        } else if (level.equals(Level.WARNING)) {
            logger.warning(message);
        }
    }

    public void info(String message) {
        logger.info(message);
    }

    public void severe(String message) {
        logger.severe(message);
    }

    public void warning(String message) {
        logger.warning(message);
    }

    public String getLogPath() {
        Date date = new Date();
        String dateToday = fileDateFormat.format(date);
        return DEFAULT_LOG_DIR + "/" + this.moduleName + "/" + dateToday + ".java.log";
    }

    public static SavantLogger getLogger(String moduleName) throws WrongModuleException {
        return new SavantLogger(moduleName);
    }

    public static void main(String[] args) {
        try {
            SavantLogger logger = SavantLogger.getLogger("streamer");
            logger.info("test java");
        } catch (WrongModuleException e) {
            e.printStackTrace();
        }
    }
}

class WrongModuleException extends Exception {

    public WrongModuleException(String message) {
        super(message);
    }
}
