
import java.io.*;
//import java.util.List ;
import java.util.Arrays ;
import java.util.ArrayList;
//import java.util.Map;
import java.util.HashMap;
//import org.json.JSONObject;  
import org.json.JSONArray; 



public class CSVtoJson implements JsonData{
//	private String CVSdata;
	public   static JSONArray AllStockData ;
	private static ArrayList<HashMap>  AllStockdataForJson=new ArrayList<HashMap>();
	
	public  static  void main(String[] args) throws IOException {		
		 new CSVtoJson();
    }
	
	
	public CSVtoJson() throws IOException{
		// get all file names in the folder
		ArrayList<String> stocknames = new ArrayList<String>();
		File[] files = new File("/home/chuan/workspace/JsonRPC2/historicalData_20days_symbol_A").listFiles();
		for (File file : files) {
		    if (file.isFile()) {
		    	stocknames.add(file.getName());
		    }
		}
		
		System.out.format("total stock files: %s \n" ,(stocknames.size()));
		// transfer CSV to Json, for each files
		for (String stockname : stocknames){
		
			AllStockdataForJson.addAll(readCVS(stockname));
			
		}
//		System.out.println(readCVS(stocknames.get(1)).get(1));
		AllStockData = new JSONArray(AllStockdataForJson);
		
		System.out.format("data entries in ALL stocks for all dates: %s \n",AllStockData.length());
		
		
		
		
	}
	
	public static JSONArray  getdata() {
		
		// get all file names in the folder
				ArrayList<String> stocknames = new ArrayList<String>();
				File[] files = new File("/home/chuan/workspace/JsonRPC2/historicalData_20days_symbol_A").listFiles();
				for (File file : files) {
				    if (file.isFile()) {
				    	stocknames.add(file.getName());
				    }
				}
				
				System.out.format("total stock files: %s \n" ,(stocknames.size()));
				// transfer CSV to Json, for each files
				for (String stockname : stocknames){
				
					AllStockdataForJson.addAll(readCVS(stockname));
					
				}
//				System.out.println(readCVS(stocknames.get(1)).get(1));
				AllStockData = new JSONArray(AllStockdataForJson);
				
				System.out.format("data entries in ALL stocks for all dates: %s",AllStockData.length());
				return AllStockData;
		
		
	}
	
	public static ArrayList<HashMap> readCVS(String stockname) {
		
			ArrayList<String>  stockdata=new ArrayList<String>(); //array's size can not modified, need use arraylist
			String[]  stockhead={"Date", "Open", "High", "Low", "Close","Volume","Adj\"\"Close"};
			ArrayList<HashMap>  stockdataForJson=new ArrayList<HashMap>();
			String cvsFile = "/home/chuan/workspace/JsonRPC2/historicalData_20days_symbol_A/"+stockname;
			BufferedReader buff = null;
			String line = "";
			String lineNoSpace = "";
			HashMap<String, String> stockdataTemp = new HashMap<>();

			
			try {
				buff=new BufferedReader (new FileReader(cvsFile));
				
				while ((line = buff.readLine()) != null) {	
					lineNoSpace=line.replace(" ", ""); //line is a string
//					System.out.println(lineNoSpace);
					
					if ( !(lineNoSpace.contains("Date"))) {
//						stockhead=lineNoSpace.split(",");	// only String[] can be assigned, not ArrayList
//					}else{
					stockdata.addAll(Arrays.asList(lineNoSpace.split(","))); //add one day's data to a arraylist obj
			
					for(int i= 0; i < stockhead.length; i++){
						stockdataTemp.put(stockhead[i],stockdata.get(i));
						stockdataTemp.put("name",stockname.replace("historicalDATA_", "").replace(".csv", "")); //add stock name to each day's data
						stockdataForJson.add(stockdataTemp);
					}
					}
					
				}
				} catch (FileNotFoundException e) {
					e.printStackTrace();
				} catch (IOException e) {
					e.printStackTrace();
				} finally {
					if (buff != null) {
						try {
							buff.close();
						} catch (IOException e) {
							e.printStackTrace();
						}
					}
				}
			
		System.out.println("Done with CVS files reading");
//		System.out.println(stockdataForJson);
		return stockdataForJson;
		}
	
		
			
		
		
	
//	public JSONObject transfer(String stock) {
//		
//		
//		
//	}
	
	
	public void go(){
		
//		BufferedReader.readLine();
//		String.split(",");	
		
	}

	
	
	
	
	
	
	

}
