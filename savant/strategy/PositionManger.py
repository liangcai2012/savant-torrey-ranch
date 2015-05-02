import os
class PositionManger:
    def __init__(self, listSymbols):
         self.__Rows = dict()
         for s in listSymbols:
             self.__Rows[s] = self.getPositionRecordTemplate(s)
    def init(self, listSymbols):
        for s in listSymbols:
            self.__Rows[s] = self.getPositionRecordTemplate(s)

        pass
    def getPositionRecords(self):
        return  self.__Rows
    def getPositionRecordTemplate(self, symbol):
        openBuyPosition={"orderId": "tobeset","shares":0, "price":0}
        closeSellPosition={"orderId": "tobeset", "shares":0, "price":0}
        posRecords = {"Symbol":symbol, \
                      "positionHold": 0,\
                      "openBuyPosition":openBuyPosition, \
                      "closeSellPosition":closeSellPosition, \
                      "stratedyId":0, \
                      "currentStage":0}
        return posRecords


if __name__ == "__main__":
     p = os.path.realpath(__file__)
     print(p)
     posM = PositionManger()
     posM.init(["spy", "qqqq"])
     r = posM.getPositionRecordTemplate("spy")
     print(r)
