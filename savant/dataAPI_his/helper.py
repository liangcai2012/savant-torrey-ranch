import os
def GetCurrentScriptFileDirectory():
    currentScriptFileDirectory= os.path.dirname(__file__)
    return currentScriptFileDirectory
def GetDataFileDirectory():
    currentScriptFileDirectory = GetCurrentScriptFileDirectory()
    dataFileDirectory = currentScriptFileDirectory +"/../data"
    return dataFileDirectory
def GetDataFileFullPath(symbol, strDate):
    # todo map (symbol, strDate)==> full path of the data file.
    # at the mean time hardcode to file qqq_trade.txt
    fullpath = GetDataFileDirectory()
    fullpath += "/qqq_trade.txt"
    return fullpath
if __name__ == "__main__":
    d = GetDataFileDirectory()
    fp = GetDataFileFullPath("qqq", "05/01/2015")
    print(d)