/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package t_json;

import java.io.IOException;
import java.io.StringWriter;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import com.google.gson.Gson;
import java.util.Date;

/**
 *
 * @author kcai
 */
public class GoogleGson implements ITest{
    @Override
    public void init()
    {
        Record r = new Record();
        r.init();
        sourceObject=r.getData();
         gson = new Gson();
         
    }
     public String name()
     {
         return "test com.google.gson";
     }
    @Override
    public void test_map2JSON()
    {   
     StringWriter   out = new StringWriter();
    gson.toJson(sourceObject, out);
   String jsonText = out.toString();
   //System.out.print(jsonText);
        
    }
     
      Map sourceObject;
      Gson gson;
         
}
