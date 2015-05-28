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
        symbol = parameters["symbol"]
        startDay = parameters["startDay"]
        endDay = parameters["endDay"]
        self.HistoricalDataReader = HistoricalDataReader.HistoricalDataReader(symbol, startDay, endDay)
    def update(self, interval, bar_mask, ma_mask):
         return  self.HistoricalDataReader.update(interval, bar_mask, ma_mask)


if __name__ == "__main__":
    parameters = {"symbol": "spy","startDay":"12/20/2014", "endDay":"12/20/2014"}
    data = DataAPIImp("backtest", None, None, parameters)

    try:
        ret = data.update(1, "", "")
        print(ret)
    except dataAPI.DataError, e:
            print(e)