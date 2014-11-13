package atapi.wrapper;

public interface APICallback {
	public void onLoginResponse(long reqid, int rc);
	public void onStatusChange(int types);

}
