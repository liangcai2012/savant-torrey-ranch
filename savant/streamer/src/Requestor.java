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
	public Requestor(APISession apiSession, Streamer streamer) 
	{
		super(apiSession.GetServerAPI(), apiSession.GetSession(), streamer);
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
		
		System.out.println("RECV (" + origRequest +"): Quote stream response [" + strResponseType + "]");
		
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
				
				System.out.println("\tsymbol:" + new String(atDataItem.symbol.symbol)+ " symbolStatus: " + strSymbolStatus);
			}
		}		
	}
}
