import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Properties;
import java.util.logging.Logger;

public class SavantConfig extends Properties {
    public final static String DEFAULT_CONFIG_PATH;
    private static Logger log;
    private String configFilePath;

    static {
        log = Logger.getLogger(SavantConfig.class.getName());

        String currentFilePath = SavantConfig.class.getProtectionDomain().getCodeSource().getLocation().getPath();
        int index = currentFilePath.indexOf("config");
        DEFAULT_CONFIG_PATH = currentFilePath.substring(0,index) + "config/default_settings.ini";
    }

    private SavantConfig(String filePath) {
        configFilePath = filePath;
        readConfig();
    }

    private SavantConfig() {
        configFilePath = DEFAULT_CONFIG_PATH;
        readConfig();
    }

    private void readConfig() {
        FileInputStream f;
        try {
            f = new FileInputStream(this.configFilePath);
            load(f);
            f.close();
        } catch (FileNotFoundException e) {
            log.severe("Could not read config: config file not found");
        } catch (IOException e) {
            log.severe("Could not read config: bad io");
        }
    }

    public String getProperty(String key) {
        return super.getProperty(key).replace("\'","");
    }

    public static SavantConfig getConfig() {
        SavantConfig config = new SavantConfig();
        return config;
    }

    public static SavantConfig getConfig(String filePath) {
        SavantConfig config = new SavantConfig(filePath);
        return config;
    }

}

