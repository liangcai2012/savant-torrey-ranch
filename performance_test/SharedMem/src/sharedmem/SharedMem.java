/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package sharedmem;

import static sharedmem.MMWriter.Init;
import static sharedmem.MMWriter.main_test_write_speed;

/**
 *
 * @author zhiqincz
 */
public class SharedMem {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        String testCase = args[0];
         System.out.println(String.format("testCase: %s", testCase));
        if(testCase.equalsIgnoreCase("writeSpeed"))
        {
           
            main_writespeed(args);
        }
        else if(testCase.equalsIgnoreCase("transferspeed"))
        {
            main_transferspeed(args);
           
        }
        
    }
     public static void main_transferspeed(String[] args)
     {
         for(int i = 0; i < 100; i++)
         {
          MMWriter.main_test_transfter_speed(args);
         }
     }
    public static void main_writespeed(String[] args)
    {
    MMWriter.Init();
        try
        {
        MMWriter.main_test_write_speed(args);
        }
        catch(Exception e)
        {
        
        }
    }
    
}
