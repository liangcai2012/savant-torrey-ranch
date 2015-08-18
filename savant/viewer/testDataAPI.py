from savant import dataAPI
import time

api = dataAPI.getDataAPI("test", "any")
api.subscribeRealtime(["QQQ", "QCOM"])
while True:
	print api.update("1s", "111111", "")
	time.sleep(1)
