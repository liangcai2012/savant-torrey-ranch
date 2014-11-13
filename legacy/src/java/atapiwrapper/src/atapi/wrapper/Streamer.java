package atapi.wrapper;

import java.util.HashMap;
import java.util.Map;

import at.feedapi.ActiveTickServerAPI;
import at.feedapi.ActiveTickStreamListener;
import at.feedapi.Session;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATGUID;
import at.utils.jlib.PrintfFormat;

public class Streamer extends ActiveTickStreamListener
{
	APISession m_session;
	
	public Streamer(APISession session)
	{
		super(session.GetSession(), false);
		m_session = session;
	}
	
	public void OnATStreamTradeUpdate(ATServerAPIDefines.ATQUOTESTREAM_TRADE_UPDATE update)
	{		
		String strSymbol = new String(update.symbol.symbol);
		int plainSymbolIndex = strSymbol.indexOf((byte)0);
		strSymbol = strSymbol.substring(0, plainSymbolIndex);
		
		StringBuffer sb = new StringBuffer();
		sb.append("[");
		sb.append(update.lastDateTime.hour);
		sb.append(":");
		sb.append(update.lastDateTime.minute);
		sb.append(":");
		sb.append(update.lastDateTime.second);
		sb.append(":");
		sb.append(update.lastDateTime.milliseconds);
		sb.append("] STREAMTRADE [symbol:");
		sb.append(strSymbol);
		sb.append(" last:");
		
		String strFormat = "%0." + update.lastPrice.precision + "f";
		sb.append(new PrintfFormat(strFormat).sprintf(update.lastPrice.price));
		sb.append(" lastSize:");
		sb.append(update.lastSize);		
		sb.append("]");
		System.out.println(sb.toString());
	}
	
	public void OnATStreamQuoteUpdate(ATServerAPIDefines.ATQUOTESTREAM_QUOTE_UPDATE update) 
	{
		String strSymbol = new String(update.symbol.symbol);
		int plainSymbolIndex = strSymbol.indexOf((byte)0);
		strSymbol = strSymbol.substring(0, plainSymbolIndex);
		StringBuffer sb = new StringBuffer();
		sb.append("[");
		sb.append(update.quoteDateTime.hour);
		sb.append(":");
		sb.append(update.quoteDateTime.minute);
		sb.append(":");
		sb.append(update.quoteDateTime.second);
		sb.append(":");
		sb.append(update.quoteDateTime.milliseconds);
		sb.append("] STREAMQUOTE [symbol:");
		sb.append(strSymbol);
		sb.append(" bid:");
		String strFormat = "%0." + update.bidPrice.precision + "f";
		sb.append(new PrintfFormat(strFormat).sprintf(update.bidPrice.price));
		sb.append(" ask:");
		strFormat = "%0." + update.askPrice.precision + "f";
		sb.append(new PrintfFormat(strFormat).sprintf(update.askPrice.price));
		sb.append(" bidSize:");
		sb.append(update.bidSize);
		sb.append(" askSize:");
		sb.append(update.askSize);
		sb.append("]");
		System.out.println(sb.toString());	
	}

	public void OnATStreamTopMarketMoversUpdate(ATServerAPIDefines.ATMARKET_MOVERS_STREAM_UPDATE update) 
	{
		String strSymbol = new String(update.marketMovers.symbol.symbol);
		int plainSymbolIndex = strSymbol.indexOf((byte)0);
		strSymbol = strSymbol.substring(0, plainSymbolIndex);
		StringBuffer sb = new StringBuffer();
		sb.append("RECV: [");
		sb.append(update.lastUpdateTime.hour);
		sb.append(":");
		sb.append(update.lastUpdateTime.minute);
		sb.append(":");
		sb.append(update.lastUpdateTime.second);
		sb.append(":");
		sb.append(update.lastUpdateTime.milliseconds);
		sb.append("] STREAMMOVERS [symbol:");
		sb.append(strSymbol);
		sb.append("]");
		System.out.println(sb.toString());
		
		String strFormat = "";
		for(int i = 0; i < update.marketMovers.items.length; i++)
		{
			StringBuilder sb2 = new StringBuilder();
			String strItemSymbol = new String(update.marketMovers.items[i].symbol.symbol);
			int plainItemSymbolIndex = strItemSymbol.indexOf((byte)0);
			strItemSymbol = strItemSymbol.substring(0, plainItemSymbolIndex);

			sb2.append("symbol:");
			sb2.append(strItemSymbol);
			
			strFormat = "%0." + update.marketMovers.items[i].lastPrice.precision + "f";
			sb2.append("  \t[last:" + new PrintfFormat(strFormat).sprintf(update.marketMovers.items[i].lastPrice.price));
			
			sb2.append(" volume:");
			sb2.append(update.marketMovers.items[i].volume);
			System.out.println(sb2.toString());
		}
		
		System.out.println("-------------------------------------------------------");
	}
}
