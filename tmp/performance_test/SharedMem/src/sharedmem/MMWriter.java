/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package sharedmem;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.text.DecimalFormat;


public class MMWriter {

 public static void main(String[] args) throws FileNotFoundException, IOException, InterruptedException {
  DecimalFormat numFormat = new DecimalFormat("###,###,###");
  String sValue = numFormat.format(100000000);
   Init();

   main_test_write_speed(args);
  //main_test_transfter_speed(args);
 }

public static void Init()
{
  try
  {
      File f = new File("/tmp/mm.txt");
  
    f.delete();

    fc = new RandomAccessFile(f, "rw").getChannel();
    long bufferSize=8*1000;
    mem =fc.map(FileChannel.MapMode.READ_WRITE, 0, bufferSize);
  }
  catch(Exception e)
  {
      
  }

}
public static void sleep(int ms)
{
     try
    {
         Thread.sleep(ms);
    }
    catch(Exception e)
    {
    }
}
public static void main_test_transfter_speed(String[] args)
{
    Init(); 
    long startT = System.currentTimeMillis();
     int transftercount = 0;
      byte byte_v1 = 1;
      mem.put(byte_v1);
      int loopcount = 0;
     for(;;)
     {
        loopcount++;
        

         byte byte0 = mem.get(0);
         if(byte0 == 2)
         {
            if(transftercount % 1000 == 0)
            {  
                System.out.println(transftercount);


            }
          
            if(transftercount == 0)
            {
                startT = System.currentTimeMillis();     
            
            }
            transftercount++;
             mem.put(0, byte_v1);
            
             //mem.load();
             // sleep(1);
             //mem.force();
         }
        
       
         if(transftercount >=10000)
         {
         break;
         }
          if(transftercount %2 == 0)
         sleep(1);
    }
     long endT = System.currentTimeMillis();
  long tot = endT - startT;
  long speed = transftercount * 1000/tot;
  DecimalFormat numFormat = new DecimalFormat("###,###,###");
  String sspeed = numFormat.format(speed);
  System.out.println(sspeed);
  System.out.println(loopcount);
         
     }
    


 public static void main_test_write_speed(String[] args) throws FileNotFoundException, IOException, InterruptedException {
  long bufferSize=8*1000;
  Init();
  
  int start = 0;
  long counter=1;
  long HUNDREDK=100000;
  long startT = System.currentTimeMillis();
  long noOfMessage = HUNDREDK * 100 ; 
  //long noOfMessage = HUNDREDK; 
  byte data_b = 0;
  //final byte data_br[] = new byte[] { 0, 0x1, 0x2, 0x3, 0x4, 5, 6, 7, 8, 9, 0, 0x1, 0x2, 0x3, 0x4, 5, 6, 7, 8, 9};
  mem.put(0, data_b);
  mem.putInt(1, 0x12345678);
  
  for(;;)
  {         
   if(!mem.hasRemaining())
   {
    start+=mem.position();
    mem =fc.map(FileChannel.MapMode.READ_WRITE, start, bufferSize);
   }
   mem.putLong(counter);
   //mem.put(data_b);

   //mem.put(data_br);
   counter++;
   if(counter > noOfMessage )
    break; 
  }
  long endT = System.currentTimeMillis();
  long tot = endT - startT;
  int numberOfBytesPerLong = 8;
  int numberOfMsPerSecond = 1000;
  long speed = noOfMessage  * numberOfBytesPerLong *numberOfMsPerSecond/tot;
  DecimalFormat numFormat = new DecimalFormat("###,###,###");
  String sspeed = numFormat.format(speed);
  System.out.println(String.format("No Of Message %s , Time(ms) %s ",noOfMessage, tot)) ;  
  System.out.println(String.format("Shared memory write speed(bytes/second):%s",sspeed)) ;
 }
 static MappedByteBuffer mem;
 static FileChannel fc;

}

