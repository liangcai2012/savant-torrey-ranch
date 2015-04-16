import java.util.ArrayList;
import java.util.HashMap;

import at.feedapi.ATCallback;
import at.feedapi.ActiveTickServerAPI;
import at.feedapi.Helpers;
import at.feedapi.Session;
import at.feedapi.ATCallback.ATLoginResponseCallback;
import at.feedapi.ATCallback.ATRequestTimeoutCallback;
import at.feedapi.ATCallback.ATServerTimeUpdateCallback;
import at.feedapi.ATCallback.ATSessionStatusChangeCallback;
import at.feedapi.ATCallback.ATOutputMessageCallback;
import at.utils.jlib.Errors;
import at.utils.jlib.OutputMessage;
import at.shared.ATServerAPIDefines;
import at.shared.ATServerAPIDefines.ATGUID;
import at.shared.ATServerAPIDefines.ATLOGIN_RESPONSE;
import at.shared.ATServerAPIDefines.SYSTEMTIME;

public class APISession extends ATCallback implements 
	ATLoginResponseCallback, ATServerTimeUpdateCallback, ATRequestTimeoutCallback, ATSessionStatusChangeCallback, ATOutputMessageCallback
						
{	
	at.feedapi.Session m_session;
	ActiveTickServerAPI m_serverapi;
	Requestor m_requestor;
	Streamer m_streamer;
	StreamerRun m_sr;
	
	long m_lastRequest;	
	String m_userid;
	String m_password;
	ATGUID m_apiKey;

   boolean m_loginSucceed = false;
	
	public APISession(ActiveTickServerAPI serverapi)
	{
		m_serverapi = serverapi;		
	}
	
	public ActiveTickServerAPI GetServerAPI()
	{
		return m_serverapi;
	}
	
	public at.feedapi.Session GetSession()
	{
		return m_session;
	}
	
	public Streamer GetStreamer()
	{
		return m_streamer;
	}
	
	public Requestor GetRequestor()
	{
		return m_requestor;
	}
	
	public boolean Init(ATGUID apiKey, String serverHostname, int serverPort, String userId, String password, StreamerRun srun)
	{
		if(m_session != null)
			m_serverapi.ATShutdownSession(m_session);
		
		m_session = m_serverapi.ATCreateSession();
		m_sr = srun;
		m_streamer = new Streamer(this, m_sr);
		m_requestor = new Requestor(this, m_streamer);
		
		m_userid = userId;
		m_password = password;
		m_apiKey = apiKey;
		
		long rc = m_serverapi.ATSetAPIKey(m_session, m_apiKey);

		m_session.SetServerTimeUpdateCallback(this);
		m_session.SetOutputMessageCallback(this);

		boolean initrc = false;
		if(rc == Errors.ERROR_SUCCESS)
			initrc = m_serverapi.ATInitSession(m_session, serverHostname, serverHostname, serverPort, this);
		
		System.out.println(m_serverapi.GetAPIVersionInformation());
		System.out.println("--------------------------------------------------------------------");

		return initrc;
	}

	public boolean UnInit()
	{
		if(m_session != null)
		{
			m_serverapi.ATShutdownSession(m_session);
			m_session = null;
		}
		
		return true;
	}
	
	//ATLoginResponseCallback
	public void process(Session session, long requestId, ATLOGIN_RESPONSE response)
	{
		String strLoginResponseType = "";
		switch(response.loginResponse.m_atLoginResponseType)
		{
		case ATServerAPIDefines.ATLoginResponseType.LoginResponseSuccess: strLoginResponseType = "LoginResponseSuccess"; m_loginSucceed = true; break;
		case ATServerAPIDefines.ATLoginResponseType.LoginResponseInvalidUserid: strLoginResponseType = "LoginResponseInvalidUserid"; break;
		case ATServerAPIDefines.ATLoginResponseType.LoginResponseInvalidPassword: strLoginResponseType = "LoginResponseInvalidPassword"; break;
		case ATServerAPIDefines.ATLoginResponseType.LoginResponseInvalidRequest: strLoginResponseType = "LoginResponseInvalidRequest"; break;
		case ATServerAPIDefines.ATLoginResponseType.LoginResponseLoginDenied: strLoginResponseType = "LoginResponseLoginDenied"; break;
		case ATServerAPIDefines.ATLoginResponseType.LoginResponseServerError: strLoginResponseType = "LoginResponseServerError"; break;
		default: strLoginResponseType = "unknown"; break;
		}
	
		System.out.println("RECV " + requestId + ": Login Response [" + strLoginResponseType + "]");
	}
	
	//ATServerTimeUpdateCallback
	public void process(SYSTEMTIME serverTime)
	{
	}
	
	//ATRequestTimeoutCallback
	public void process(long origRequest)
	{
		System.out.println("(" + origRequest + "): Request timed-out\n");
	}
	
	//ATSessionStatusChangeCallback
	public void process(at.feedapi.Session session, ATServerAPIDefines.ATSessionStatusType type)
	{
		String strStatusType = "";
		switch(type.m_atSessionStatusType)
		{
		case ATServerAPIDefines.ATSessionStatusType.SessionStatusConnected: strStatusType = "SessionStatusConnected"; break;
		case ATServerAPIDefines.ATSessionStatusType.SessionStatusDisconnected: strStatusType = "SessionStatusDisconnected"; break;
		case ATServerAPIDefines.ATSessionStatusType.SessionStatusDisconnectedDuplicateLogin: strStatusType = "SessionStatusDisconnectedDuplicateLogin"; break;
		default: break;
		}

		System.out.println("RECV Status change [" + strStatusType + "]");
		
		//if we are connected to the server, send a login request
		if(type.m_atSessionStatusType == ATServerAPIDefines.ATSessionStatusType.SessionStatusConnected)
		{
			m_lastRequest = m_serverapi.ATCreateLoginRequest(session, m_userid, m_password, this);			
			boolean rc = m_serverapi.ATSendRequest(session, m_lastRequest, ActiveTickServerAPI.DEFAULT_REQUEST_TIMEOUT, this);
			
			System.out.println("SEND (" + m_lastRequest + "): Login request [" + m_userid + "] (rc = " + (char)Helpers.ConvertBooleanToByte(rc) + ")");
		}
	}
	
	public void process(OutputMessage outputMessage)
	{
		System.out.println(outputMessage.GetMessage());
	}
}
