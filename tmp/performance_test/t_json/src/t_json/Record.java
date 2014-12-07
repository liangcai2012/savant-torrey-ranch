/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package t_json;

import java.util.Date;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 *
 * @author kcai
 */
public class Record {
     void init()
    {
        sourceObject=new LinkedHashMap();
   
       Date date = new Date();
     sourceObject.put("time",date);
    sourceObject.put("num1",new Integer(100));
    sourceObject.put("num2",new Integer(100));
    sourceObject.put("num3",new Integer(100));
    sourceObject.put("num4",new Integer(100));
    sourceObject.put("num5",new Integer(100));
    sourceObject.put("num6",new Integer(100));

    sourceObject.put("balance1",new Double(1000.21));
    sourceObject.put("balance2",new Double(1000.21));
    sourceObject.put("balance3",new Double(1000.21));
    }
     
     Map getData()
     {
         return sourceObject;
     }
    
    Map sourceObject;
    
}
