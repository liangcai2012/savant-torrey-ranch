/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package t_json;

import java.io.IOException;
import java.io.StringWriter;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.simple.JSONValue;

/**
 *
 * @author kcai
 */
public class simpleJson implements ITest{
    @Override
    public void init()
    {
     Record r = new Record();
        r.init();
        sourceObject=r.getData();  
        
    }
     public String name()
     {
         return "test org.json.simple";
     }
    @Override
    public void test_map2JSON()
    {
        StringWriter   out = new StringWriter();

        try {
            JSONValue.writeJSONString(sourceObject, out);
        } catch (IOException ex) {
            Logger.getLogger(simpleJson.class.getName()).log(Level.SEVERE, null, ex);
        }
   String jsonText = out.toString();
   //System.out.print(jsonText);
        
    }
    
    Map sourceObject;
     
}
