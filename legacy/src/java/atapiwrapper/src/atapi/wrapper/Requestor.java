package atapi.wrapper;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Iterator;
import java.util.Vector;

import at.feedapi.Helpers;
import at.utils.jlib.PrintfFormat;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATBarHistoryResponseType;
import at.shared.ATServerAPIDefines.ATDataType;
import at.shared.ATServerAPIDefines.ATMarketMoversDbResponseType;
import at.shared.ATServerAPIDefines.ATQuoteDbResponseType;
import at.shared.ATServerAPIDefines.ATStreamResponseType;
import at.shared.ATServerAPIDefines.ATSymbolStatus;
import at.shared.ATServerAPIDefines.ATTICKHISTORY_QUOTE_RECORD;
import at.shared.ATServerAPIDefines.ATTICKHISTORY_TRADE_RECORD;
import at.shared.ATServerAPIDefines.ATTickHistoryRecordType;
import at.shared.ATServerAPIDefines.ATTickHistoryResponseType;
import at.shared.ATServerAPIDefines.QuoteDbDataItem;
import at.shared.ATServerAPIDefines.QuoteDbResponseItem;
import at.shared.ATServerAPIDefines.SYSTEMTIME;
import at.shared.ActiveTick.*;

public class Requestor extends at.feedapi.ActiveTickServerRequester
{
	APIReqCallback m_rcb;
	
	public Requestor(APISession apiSession, Streamer streamer, APIReqCallback rcb) 
	{
		super(apiSession.GetServerAPI(), apiSession.GetSession(), streamer);
		m_rcb = rcb;
	}
	
	public void OnQuoteDbResponse(long origRequest, ATServerAPIDefines.ATQuoteDbResponseType responseType, Vector<ATServerAPIDefines.QuoteDbResponseItem> vecData)
	{
		String strResponseType = "";
		switch(responseType.m_atQuoteDbResponseType)
		{
			case ATQuoteDbResponseType.QuoteDbResponseSuccess:
				strResponseType = "QuoteDbResponseSuccess";
			break;
			case ATQuoteDbResponseType.QuoteDbResponseInvalidRequest:
				strResponseType = "QuoteDbResponseInvalidRequest";
			break;
			case ATQuoteDbResponseType.QuoteDbResponseDenied:
				strResponseType = "QuoteDbResponseDenied";
			break;
		}
		System.out.println("RECV (" + origRequest +"): QuoteDb response " + strResponseType + "\n-------------------------------------------------------------------------");

		Iterator<QuoteDbResponseItem> itr = vecData.iterator();
		String strSymbolStatus = "";
		while(itr.hasNext())
		{
			QuoteDbResponseItem responseItem = (QuoteDbResponseItem)itr.next();
			switch(responseItem.m_atResponse.status.m_atSymbolStatus)
			{
				case ATSymbolStatus.SymbolStatusSuccess: strSymbolStatus = "SymbolStatusSuccess"; break;
				case ATSymbolStatus.SymbolStatusInvalid: strSymbolStatus = "SymbolStatusInvalid"; break;
				case ATSymbolStatus.SymbolStatusUnavailable: strSymbolStatus = "SymbolStatusUnavailable"; break;
				case ATSymbolStatus.SymbolStatusNoPermission: strSymbolStatus = "SymbolStatusNoPermission"; break;
			}
			String strItemSymbol = new String(responseItem.m_atResponse.symbol.symbol);
			int plainItemSymbolIndex = strItemSymbol.indexOf((byte)0);
			strItemSymbol = strItemSymbol.substring(0, plainItemSymbolIndex);

			System.out.println("\tsymbol: [" + strItemSymbol + "] symbolStatus: " + strSymbolStatus);
			
			Iterator<QuoteDbDataItem> itrDataItems = responseItem.m_vecDataItems.iterator();
			while(responseItem.m_atResponse.status.m_atSymbolStatus == ATSymbolStatus.SymbolStatusSuccess && itrDataItems.hasNext())
			{
				QuoteDbDataItem dataItem = (QuoteDbDataItem)itrDataItems.next();
				String strData = "";
				byte[] intBytes = new byte[4];
				byte[] longBytes = new byte[8];

				switch(dataItem.m_dataItem.dataType.m_atDataType)
				{
					case ATDataType.Byte:
						strData = new String(dataItem.GetItemData());
						break;
					case ATDataType.ByteArray:
						strData = new String("byte data");
						break;
					case ATDataType.UInteger32:
					{
						System.arraycopy(dataItem.GetItemData(), 0, intBytes, 0, 4);
						int nData = ByteBuffer.wrap(intBytes).order(ByteOrder.LITTLE_ENDIAN).getInt();
						strData = new String("" + nData);
					}
					break;
					case ATDataType.UInteger64:
					{
						System.arraycopy(dataItem.GetItemData(), 0, longBytes, 0, 8);
						long nData = ByteBuffer.wrap(longBytes).order(ByteOrder.LITTLE_ENDIAN).getLong();
						strData = new String("" + nData);
					}
					break;
					case ATDataType.Integer32:
					{
						System.arraycopy(dataItem.GetItemData(), 0, intBytes, 0, 4);
						int nData = ByteBuffer.wrap(intBytes).order(ByteOrder.LITTLE_ENDIAN).getInt();
						strData = new String("" + nData);
					}
					break;
					case ATDataType.Integer64:
					{
						System.arraycopy(dataItem.GetItemData(), 0, longBytes, 0, 8);
						long nData = ByteBuffer.wrap(longBytes).order(ByteOrder.LITTLE_ENDIAN).getLong();
						strData = new String("" + nData);
					}
					break;
					case ATDataType.Price:
						{
							ATServerAPIDefines.ATPRICE price = Helpers.BytesToPrice(dataItem.GetItemData());
							strData = "" + price.price;
						}
						break;
					case ATDataType.String:
						{
							strData = new String(dataItem.GetItemData());
						}
						break;
					case ATDataType.UnicodeString:
						{
							strData = new String(dataItem.GetItemData());
						}
						break;
					case ATDataType.DateTime:
						{
							UInt64 li = new UInt64(dataItem.GetItemData());
							SYSTEMTIME dateTime = DateTime.GetDateTime(li);
							StringBuilder sb = new StringBuilder();
							sb.append(dateTime.month);
							sb.append("/");
							sb.append(dateTime.day);
							sb.append("/");
							sb.append(dateTime.year);
							sb.append(" ");
							sb.append(dateTime.hour);
							sb.append(":");
							sb.append(dateTime.minute);
							sb.append(":");
							sb.append(dateTime.second);
							strData = sb.toString();
						}
						break;
	                default: 
	                	break;
				}

				StringBuilder sb = new StringBuilder();
				sb.append("\tATQuoteFieldType:" + dataItem.m_dataItem.fieldType.m_atQuoteFieldType + "\n");
				sb.append("\tATFieldStatus:" + dataItem.m_dataItem.fieldStatus.m_atFieldStatus + "\n");
				sb.append("\tATDataType:" + dataItem.m_dataItem.dataType.m_atDataType + "\n");
				sb.append("\tData:" + strData);
				System.out.println(sb.toString());
			}
			System.out.println("\t-------------------------------------");
		}
	}
	
	public void OnRequestTimeoutCallback(long origRequest)
	{
		System.out.println("(" + origRequest + "): Request timed-out");
	}

	public void OnQuoteStreamResponse(long origRequest, ATServerAPIDefines.ATStreamResponseType responseType, Vector<ATServerAPIDefines.ATQUOTESTREAM_DATA_ITEM> vecData)
	{
		String strResponseType = "";
		switch(responseType.m_responseType)
		{
			case ATStreamResponseType.StreamResponseSuccess: strResponseType = "StreamResponseSuccess"; break;
			case ATStreamResponseType.StreamResponseInvalidRequest: strResponseType = "StreamResponseInvalidRequest"; break;
			case ATStreamResponseType.StreamResponseDenied: strResponseType = "StreamResponseDenied"; break;
			default: break;
		}
		
		System.out.println("RECV (" + origRequest +"): Quote stream response [" + strResponseType + "]\n--------------------------------------------------------------");
		
		if(responseType.m_responseType == ATStreamResponseType.StreamResponseSuccess)
		{
			String strSymbolStatus = "";
			Iterator<ATServerAPIDefines.ATQUOTESTREAM_DATA_ITEM> itrDataItems = vecData.iterator();
			while(itrDataItems.hasNext())
			{
				ATServerAPIDefines.ATQUOTESTREAM_DATA_ITEM atDataItem = (ATServerAPIDefines.ATQUOTESTREAM_DATA_ITEM)itrDataItems.next();
				switch(atDataItem.symbolStatus.m_atSymbolStatus)
				{
					case ATSymbolStatus.SymbolStatusSuccess: strSymbolStatus = "SymbolStatusSuccess"; break;
					case ATSymbolStatus.SymbolStatusInvalid: strSymbolStatus = "SymbolStatusInvalid"; break;
					case ATSymbolStatus.SymbolStatusUnavailable: strSymbolStatus = "SymbolStatusUnavailable"; break;
					case ATSymbolStatus.SymbolStatusNoPermission: strSymbolStatus = "SymbolStatusNoPermission"; break;
					default: break;
				}
				
				System.out.println("\tsymbol:" + strSymbolStatus + " symbolStatus: " + strSymbolStatus);
			}
		}		
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
		m_rcb.onBarHistoryDbReady(origRequest, strResponseType, vecData);
		/*
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
	*/
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
		
		//System.out.println("RECV (" + origRequest +"): Tick history response [" + strResponseType + "]\n--------------------------------------------------------------");

		m_rcb.onTickHistoryDbReady(origRequest, strResponseType, vecData);
		/*
		
		Iterator<ATServerAPIDefines.ATTICKHISTORY_RECORD> itrDataItems = vecData.iterator();
		int index = 0;
		int recCount = vecData.size();
		
		String strFormat = "%0.2f";
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
					System.out.println(sb.toString());
				}
				break;
				case ATTickHistoryRecordType.TickHistoryRecordQuote:
				{
					ATTICKHISTORY_QUOTE_RECORD atQuoteRecord = (ATTICKHISTORY_QUOTE_RECORD)record; 
					StringBuilder sb = new StringBuilder();
					sb.append("[");
					sb.append(++index);
					sb.append("/");
					sb.append(recCount);
					sb.append("]");
					sb.append(" [" + atQuoteRecord.quoteDateTime.month+ "/" + atQuoteRecord.quoteDateTime.day + "/" + atQuoteRecord.quoteDateTime.year + " ");
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
					System.out.println(sb.toString());
				}
				break;
			}
		}
		System.out.println("--------------------------------------------------------------\nTotal records:" + recCount);
		*/
	}

	public void OnMarketHolidaysResponse(long origRequest, Vector<ATServerAPIDefines.ATMARKET_HOLIDAYSLIST_ITEM> vecData)
	{
		System.out.println("RECV (" + origRequest +"): MarketHolidays response \n--------------------------------------------------------------");
		Iterator<ATServerAPIDefines.ATMARKET_HOLIDAYSLIST_ITEM> itrDataItems = vecData.iterator();
		
		int index = 0;
		int recCount = vecData.size();
		
		while(itrDataItems.hasNext())
		{	
			ATServerAPIDefines.ATMARKET_HOLIDAYSLIST_ITEM item = (ATServerAPIDefines.ATMARKET_HOLIDAYSLIST_ITEM)itrDataItems.next();
			StringBuilder sb = new StringBuilder();
			sb.append("[");
			sb.append(++index);
			sb.append("/");
			sb.append(recCount);
			sb.append("]");
			sb.append(" [" + item.beginDateTime.month+ "/" + item.beginDateTime.day + "/" + item.beginDateTime.year + " ");
			sb.append(item.beginDateTime.hour + ":" + item.beginDateTime.minute + ":" + item.beginDateTime.second + "] ");
			sb.append(" - ");
			sb.append(" [" + item.endDateTime.month+ "/" + item.endDateTime.day + "/" + item.endDateTime.year + " ");
			sb.append(item.endDateTime.hour + ":" + item.endDateTime.minute + ":" + item.endDateTime.second + "] ");
			if( (item.endDateTime.day == item.beginDateTime.day) &&
				(item.endDateTime.hour - item.beginDateTime.hour >= 8))
			{
				sb.append(" -- ALL DAY ");
			}
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
	
	public void OnMarketMoversStreamResponse(long origRequest, ATServerAPIDefines.ATStreamResponseType responseType, ATServerAPIDefines.ATMARKET_MOVERS_STREAM_RESPONSE response)
	{
		String strResponseType = "";
		switch(responseType.m_responseType)
		{
			case ATStreamResponseType.StreamResponseSuccess: strResponseType = "StreamResponseSuccess"; break;
			case ATStreamResponseType.StreamResponseInvalidRequest: strResponseType = "StreamResponseInvalidRequest"; break;
			case ATStreamResponseType.StreamResponseDenied: strResponseType = "StreamResponseDenied"; break;
			default: break;
		}
		System.out.println("RECV (" + origRequest +"): Market Movers response [ " + strResponseType + "]\n--------------------------------------------------------------");
	}
	
	public void OnConstituentListResponse(long origRequest, Vector<ATServerAPIDefines.ATSYMBOL> vecData)
	{
		String strResponseType = "";
		
		for(int i = 0; i < vecData.size(); ++i)
		{
			String symbol = Helpers.SymbolToString(vecData.elementAt(i));
			strResponseType += symbol +"\n";			
		}
		
		System.out.println("RECV (" + origRequest +"): Constituent list response [ " + strResponseType + "]\n--------------------------------------------------------------");
	}
	public long SendATTickHistoryDbRequest1(ATServerAPIDefines.ATSYMBOL symbol, boolean selectTrades, boolean selectQuotes, ATServerAPIDefines.SYSTEMTIME beginDateTime, ATServerAPIDefines.SYSTEMTIME endDateTime, int timeout)
	{
		return super.SendATTickHistoryDbRequest(symbol, selectTrades, selectQuotes,beginDateTime, endDateTime, timeout);
	}
}
