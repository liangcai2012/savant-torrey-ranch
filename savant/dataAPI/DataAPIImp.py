import dataAPI
import HistoricalDataReader
import os
class DataAPIImp(dataAPI.DataAPI):
    # parameters is a dictionary which has entries.
    # the keys are:"symbol","startDay", "endDay"eg.
    # {"symbol": "spy","startDay":"12/20/2014", "endDay":"12/20/2014"}
    def __init__(self, clientName, serverIP= None, port= None, parameters= None):
        self.clientName = clientName
        self.serverIP = serverIP
        self.port = port
        self.parameters = parameters
        symbols = parameters["symbol"]
        startDay = parameters["startDay"]
        endDay = parameters["endDay"]
        self.symbol2HDR = {}
        for symbol in symbols:
            hdr = HistoricalDataReader.HistoricalDataReader(symbol, startDay, endDay)
            self.symbol2HDR[symbol] = hdr
    def update(self, interval, bar_mask, ma_mask):
        ret = {}
        for k in self.symbol2HDR.keys():
            ret[k] = self.symbol2HDR[k].update(interval, bar_mask, ma_mask)

        return ret


if __name__ == "__main__":
    parameters = {"symbol": ["spy", "qqq"],"startDay":"12/01/2014", "endDay":"12/01/2014"}
    data = DataAPIImp("backtest", None, None, parameters)

    try:
        ret = data.update(1, "", "")
        print(ret)
    except dataAPI.DataError, e:
            print(e)