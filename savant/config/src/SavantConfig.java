import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Properties;
import java.util.logging.Logger;

public class SavantConfig extends Properties {
    private final static String DEFAULT_CONFIG_PATH;
    private static Logger log;
    private String configFilePath;

    static {
        log = Logger.getLogger(SavantConfig.class.getName());

        String currentFilePath = new File("").getAbsolutePath();
        DEFAULT_CONFIG_PATH = currentFilePath + "/default_settings.ini";
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

    public static SavantConfig getConfig() {
        SavantConfig config = new SavantConfig();
        return config;
    }

    public static SavantConfig getConfig(String filePath) {
        SavantConfig config = new SavantConfig(filePath);
        return config;
    }

}

