/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package t_json;
import java.text.DecimalFormat;
import org.json.simple.JSONObject;
import com.google.gson.Gson;

/**
 *
 * @author kcai
 */
public class T_json {
          
    public static void runTest(ITest testobj)
    {
         
       long startT = System.currentTimeMillis();
       for(int i = 0; i < loopcount; i++)
       {
           if(i %onePrintPerXLoop == 0)
           {
               // print out i as an indicte to show test progress.
               System.out.println(i);
           }
           // run the test function.
           testobj.test_map2JSON();
       }
       long endT = System.currentTimeMillis();
       long elapseT = endT - startT;
       long speed = loopcount *1000L / elapseT;
       DecimalFormat numFormat = new DecimalFormat("###,###,###");
        String sspeed = numFormat.format(speed);
        System.out.println(testobj.name());
         System.out.print(sspeed);
         System.out.print(" calls / seconds\n");
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
          GoogleGson gs  = new GoogleGson();
          gs.init();
        runTest(gs);
     
        simpleJson sj = new simpleJson();
        sj.init();
        runTest(sj);
    }
     static long onePrintPerXLoop = 1000 *100; // print message every 100k loop.
    static long loopcount = 1000 *1000; // run 1 miilion time
    ITest currentTest;
    ITest googleGson;
    
    
}
