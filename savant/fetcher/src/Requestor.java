import java.io.*;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;

import at.feedapi.ActiveTickStreamListener;
import at.utils.jlib.PrintfFormat;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATBarHistoryResponseType;
import at.shared.ATServerAPIDefines.ATMarketMoversDbResponseType;
import at.shared.ATServerAPIDefines.ATTICKHISTORY_QUOTE_RECORD;
import at.shared.ATServerAPIDefines.ATTICKHISTORY_TRADE_RECORD;
import at.shared.ATServerAPIDefines.ATTickHistoryRecordType;
import at.shared.ATServerAPIDefines.ATTickHistoryResponseType;


public class Requestor extends at.feedapi.ActiveTickServerRequester
{
	ATTickDataFetcher m_fetcher;
	String premarketFilePath;
	String marketFilePath;
	String aftermarketFilePath;

	Logger logger = Logger.getLogger(ATTickDataFetcher.class.getName());

	public Requestor(APISession apiSession, ActiveTickStreamListener streamer, ATTickDataFetcher fetcher)
	{
		super(apiSession.GetServerAPI(), apiSession.GetSession(), streamer);
		m_fetcher = fetcher;
	}
	
	public void OnRequestTimeoutCallback(long origRequest)
	{
		System.out.println("(" + origRequest + "): Request timed-out");
	}

	public void OnTickHistoryDbResponse(long origRequest, ATServerAPIDefines.ATTickHistoryResponseType responseType, Vector<ATServerAPIDefines.ATTICKHISTORY_RECORD> vecData)
	{
		String strResponseType = "";
		switch(responseType.m_responseType)
		{
			case ATTickHistoryResponseType.TickHistoryResponseSuccess: strResponseType = "TickHistoryResponseSuccess"; break;
			case ATTickHistoryResponseType.TickHistoryResponseInvalidRequest: strResponseType = "TickHistoryResponseInvalidRequest"; break;
			case ATTickHistoryResponseType.TickHistoryResponseMaxLimitReached: strResponseType = "TickHistoryResponseMaxLimitReached"; break;
			case ATTickHistoryResponseType.TickHistoryResponseDenied: strResponseType = "TickHistoryResponseDenied"; break;
			default: break;
		}
		
		System.out.println("RECV (" + origRequest +"): Tick history response [" + strResponseType + "]\n--------------------------------------------------------------");

		Iterator<ATServerAPIDefines.ATTICKHISTORY_RECORD> itrDataItems = vecData.iterator();
		int index = 0;
		int recCount = vecData.size();

		if (recCount >= 100000) {
			System.out.println("Overloaded: " + recCount);
			m_fetcher.onTickHistoryOverload();
			return;
		}

		String strFormat = "%0.2f";
		ArrayList<String> premarketTickRecords = new ArrayList<String>();
		ArrayList<String> marketTickRecords = new ArrayList<String>();
		ArrayList<String> aftermarketTickRecords = new ArrayList<String>();
		while(itrDataItems.hasNext())
		{	
			ATServerAPIDefines.ATTICKHISTORY_RECORD record = (ATServerAPIDefines.ATTICKHISTORY_RECORD)itrDataItems.next();
			switch(record.recordType.m_historyRecordType)
			{
				case ATTickHistoryRecordType.TickHistoryRecordTrade:
				{
					ATTICKHISTORY_TRADE_RECORD atTradeRecord = (ATTICKHISTORY_TRADE_RECORD)record; 
					StringBuilder sb = new StringBuilder();
					sb.append("[");
					sb.append(++index);
					sb.append("/");
					sb.append(recCount);
					sb.append("]");
					sb.append(" [" + atTradeRecord.lastDateTime.month+ "/" + atTradeRecord.lastDateTime.day + "/" + atTradeRecord.lastDateTime.year + " ");
					sb.append(atTradeRecord.lastDateTime.hour + ":" + atTradeRecord.lastDateTime.minute + ":" + atTradeRecord.lastDateTime.second + "] ");
					sb.append("TRADE ");
					
					strFormat = "%0." + atTradeRecord.lastPrice.precision + "f";
					sb.append("  \t[last:" + new PrintfFormat(strFormat).sprintf(atTradeRecord.lastPrice.price));
					sb.append("  \tlastsize:" + atTradeRecord.lastSize);
					sb.append("  \tlastexch:" + atTradeRecord.lastExchange.m_atExchangeType);
					sb.append("  \tcond:" + atTradeRecord.lastCondition[0].m_atTradeConditionType);
					String hour = (atTradeRecord.lastDateTime.hour >= 10) ? String.valueOf(atTradeRecord.lastDateTime.hour) : "0" + atTradeRecord.lastDateTime.hour;
					String minute = (atTradeRecord.lastDateTime.minute >= 10) ? String.valueOf(atTradeRecord.lastDateTime.minute) : "0" + atTradeRecord.lastDateTime.minute;
					String second = (atTradeRecord.lastDateTime.second >= 10) ? String.valueOf(atTradeRecord.lastDateTime.second) : "0" + atTradeRecord.lastDateTime.second;
					String tradeTime = hour + minute + second;
					try {
						if (m_fetcher.subtractTime(tradeTime, "093000") < 0) {
							premarketTickRecords.add(sb.toString() + "\n");
						} else if (atTradeRecord.lastDateTime.hour >= 16) {
							aftermarketTickRecords.add(sb.toString() + "\n");
						} else {
							marketTickRecords.add(sb.toString() + "\n");
						}
					} catch (ParseException e) {
						System.out.println("Time parsing error");
					}
				}
				break;
				case ATTickHistoryRecordType.TickHistoryRecordQuote: {
					ATTICKHISTORY_QUOTE_RECORD atQuoteRecord = (ATTICKHISTORY_QUOTE_RECORD) record;
					StringBuilder sb = new StringBuilder();
					sb.append("[");
					sb.append(++index);
					sb.append("/");
					sb.append(recCount);
					sb.append("]");
					sb.append(" [" + atQuoteRecord.quoteDateTime.month + "/" + atQuoteRecord.quoteDateTime.day + "/" + atQuoteRecord.quoteDateTime.year + " ");
					sb.append(atQuoteRecord.quoteDateTime.hour + ":" + atQuoteRecord.quoteDateTime.minute + ":" + atQuoteRecord.quoteDateTime.second + "] ");
					sb.append("QUOTE ");

					strFormat = "%0." + atQuoteRecord.bidPrice.precision + "f";
					sb.append("  \t[bid:" + new PrintfFormat(strFormat).sprintf(atQuoteRecord.bidPrice.price));

					strFormat = "%0." + atQuoteRecord.askPrice.precision + "f";
					sb.append("  \task:" + new PrintfFormat(strFormat).sprintf(atQuoteRecord.askPrice.price) + " ");

					sb.append("  \tbidsize:" + atQuoteRecord.bidSize);
					sb.append("  \tasksize:" + atQuoteRecord.askSize);
					sb.append("  \tbidexch:" + atQuoteRecord.bidExchange.m_atExchangeType);
					sb.append("  \taskexch:" + atQuoteRecord.askExchange.m_atExchangeType);
					sb.append("  \tcond:" + atQuoteRecord.quoteCondition.m_quoteConditionType);
					String hour = (atQuoteRecord.quoteDateTime.hour >= 10) ? String.valueOf(atQuoteRecord.quoteDateTime.hour) : "0" + atQuoteRecord.quoteDateTime.hour;
					String minute = (atQuoteRecord.quoteDateTime.minute >= 10) ? String.valueOf(atQuoteRecord.quoteDateTime.minute) : "0" + atQuoteRecord.quoteDateTime.minute;
					String second = (atQuoteRecord.quoteDateTime.second >= 10) ? String.valueOf(atQuoteRecord.quoteDateTime.second) : "0" + atQuoteRecord.quoteDateTime.second;
					String tradeTime = hour + minute + second;
					try {
						if (m_fetcher.subtractTime(tradeTime, "093000") < 0) {
							premarketTickRecords.add(sb.toString() + "\n");
						} else if (atQuoteRecord.quoteDateTime.hour >= 16) {
							aftermarketTickRecords.add(sb.toString() + "\n");
						} else {
							marketTickRecords.add(sb.toString() + "\n");
						}
					} catch (ParseException e) {
						System.out.println("Time parsing error");
					}
					break;
				}
			}
		}
		if (!premarketTickRecords.isEmpty()) {
			this.writeTickRecord(this.premarketFilePath,premarketTickRecords);
		}
		if (!marketTickRecords.isEmpty()) {
			this.writeTickRecord(this.marketFilePath,marketTickRecords);
		}
		if (!aftermarketTickRecords.isEmpty()) {
			this.writeTickRecord(this.aftermarketFilePath,aftermarketTickRecords);
		}
		System.out.println("--------------------------------------------------------------\nTotal records:" + recCount);
		m_fetcher.onRequestComplete();
	}

	public void OnBarHistoryDbResponse(long origRequest, ATServerAPIDefines.ATBarHistoryResponseType responseType, Vector<ATServerAPIDefines.ATBARHISTORY_RECORD> vecData)
	{
		String strResponseType = "";
		switch(responseType.m_responseType)
		{
			case ATBarHistoryResponseType.BarHistoryResponseSuccess: strResponseType = "BarHistoryResponseSuccess"; break;
			case ATBarHistoryResponseType.BarHistoryResponseInvalidRequest: strResponseType = "BarHistoryResponseInvalidRequest"; break;
			case ATBarHistoryResponseType.BarHistoryResponseMaxLimitReached: strResponseType = "BarHistoryResponseMaxLimitReached"; break;
			case ATBarHistoryResponseType.BarHistoryResponseDenied: strResponseType = "BarHistoryResponseDenied"; break;
			default: break;
		}

		System.out.println("RECV (" + origRequest +"): Bar History response [" + strResponseType + "]\n--------------------------------------------------------------");

		Iterator<ATServerAPIDefines.ATBARHISTORY_RECORD> itrDataItems = vecData.iterator();
		int index = 0;
		int recCount = vecData.size();
		String strFormat = "%0.2f";
		while(itrDataItems.hasNext())
		{
			ATServerAPIDefines.ATBARHISTORY_RECORD record = (ATServerAPIDefines.ATBARHISTORY_RECORD)itrDataItems.next();
			StringBuilder sb = new StringBuilder();
			sb.append((++index) + "/" + recCount + " ");
			sb.append("[" + record.barTime.month + "/" + record.barTime.day + "/" + record.barTime.year + " ");
			sb.append(record.barTime.hour + ":" + record.barTime.minute + ":" + record.barTime.second + "] ");


			strFormat = "%0." + record.open.precision + "f";
			sb.append("  \t[o:" + new PrintfFormat(strFormat).sprintf(record.open.price));

			strFormat = "%0." + record.high.precision + "f";
			sb.append("  \th:" + new PrintfFormat(strFormat).sprintf(record.high.price) + " ");

			strFormat = "%0." + record.low.precision + "f";
			sb.append("  \tl:" + new PrintfFormat(strFormat).sprintf(record.low.price) + " ");

			strFormat = "%0." + record.close.precision + "f";
			sb.append("  \tc:" + new PrintfFormat(strFormat).sprintf(record.close.price) + " ");

			sb.append("  \tvol:" + record.volume);

			System.out.println(sb.toString());
		}
		System.out.println("--------------------------------------------------------------\nTotal records:" + recCount);
	}

	public void OnMarketMoversDbResponse(long origRequest, ATServerAPIDefines.ATMarketMoversDbResponseType responseType, Vector<ATServerAPIDefines.ATMARKET_MOVERS_RECORD> vecData)
	{
		String strResponseType = "";
		switch(responseType.m_responseType)
		{
			case ATMarketMoversDbResponseType.MarketMoversDbResponseSuccess: strResponseType = "MarketMoversDbResponseSuccess"; break;
			case ATMarketMoversDbResponseType.MarketMoversDbResponseInvalidRequest: strResponseType = "MarketMoversDbResponseInvalidRequest"; break;
			case ATMarketMoversDbResponseType.MarketMoversDbResponseDenied: strResponseType = "MarketMoversDbResponseDenied"; break;
			default: break;
		}
		System.out.println("RECV (" + origRequest +"): Market Movers response [ " + strResponseType + "]\n--------------------------------------------------------------");
		Iterator<ATServerAPIDefines.ATMARKET_MOVERS_RECORD> itrMarketMovers = vecData.iterator();
		String strFormat = "";
		while(itrMarketMovers.hasNext())
		{
			ATServerAPIDefines.ATMARKET_MOVERS_RECORD record = (ATServerAPIDefines.ATMARKET_MOVERS_RECORD)itrMarketMovers.next();
			String strSymbol = new String(record.symbol.symbol);
			int plainSymbolIndex = strSymbol.indexOf((byte)0);
			if(plainSymbolIndex > 0)
				strSymbol = strSymbol.substring(0, plainSymbolIndex);

			System.out.println("Market movers symbol: " + strSymbol + "\n------------------\n");
			for(int i = 0; i < record.items.length; i++)
			{
				String strItemSymbol = new String(record.items[i].symbol.symbol);
				int plainItemSymbolIndex = strItemSymbol.indexOf((byte)0);
				if(plainItemSymbolIndex > 0)
					strItemSymbol = strItemSymbol.substring(0, plainItemSymbolIndex);
				else
					strItemSymbol = "";
				

				StringBuilder sb = new StringBuilder();
				sb.append("symbol:");
				sb.append(strItemSymbol);
				
				strFormat = "%0." + record.items[i].lastPrice.precision + "f";
				sb.append("  \tlast:" + new PrintfFormat(strFormat).sprintf(record.items[i].lastPrice.price));
				
				sb.append(" volume:");
				sb.append(record.items[i].volume);

				String strName = new String(record.items[i].name);
				int plainNameIndex = strName.indexOf((byte)0);
				if(plainNameIndex > 0)
					strName = strName.substring(0, plainNameIndex-1);
				else
					strName = "";

				sb.append(" name: " + strName);
				System.out.println(sb.toString());
			}			
		}		
	}

	public void writeTickRecord(String filepath, ArrayList<String> records)
	{
		try {
            /*
			FileOutputStream dest = new FileOutputStream(filepath);
			ZipOutputStream writer = new ZipOutputStream(new BufferedOutputStream(dest));
			ZipEntry entry = new ZipEntry("data.tsv");
			writer.putNextEntry(entry);
            */
			File data = new File(filepath);
			if (!data.exists()) {
				data.createNewFile();
			}
			FileWriter fw = new FileWriter(data,true);
			BufferedWriter writer = new BufferedWriter(fw);
			for (String record : records) {
				//writer.write(record.getBytes(), 0, record.length());
                writer.write(record+"\n");
			}
			writer.close();

		} catch (IOException e) {
			System.out.println("Cannot write to file");
		}
	}

	public void setOutputPath(String premarketFilePath, String marketFilePath, String aftermarketFilePath) {
		this.premarketFilePath = premarketFilePath;
		this.marketFilePath = marketFilePath;
		this.aftermarketFilePath = aftermarketFilePath;
	}
}