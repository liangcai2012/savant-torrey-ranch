package atapi.wrapper;

import java.util.Vector;

import at.shared.ATServerAPIDefines;

public interface APIReqCallback {
	public void onTickHistoryDbReady(long reqid, String rep, Vector<ATServerAPIDefines.ATTICKHISTORY_RECORD> vecData);
	public void onBarHistoryDbReady(long reqid, String rep, Vector<ATServerAPIDefines.ATBARHISTORY_RECORD> vecData);

}
