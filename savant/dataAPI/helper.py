import os
def GetCurrentScriptFileDirectory():
    currentScriptFileDirectory= os.path.dirname(__file__)
    return currentScriptFileDirectory
def GetDataFileDirectory():
    currentScriptFileDirectory = GetCurrentScriptFileDirectory()
    dataFileDirectory = currentScriptFileDirectory +"/../data/"
    return dataFileDirectory
def GetDataFileFullPath(symbol, strDate):
    # todo map (symbol, strDate)==> full path of the data file.
    # at the mean time hardcode to file qqq_trade.txt
    fullpath = GetDataFileDirectory()
    filename = symbol + "_trade_" + strDate.replace("/", "") + ".txt"
    #filename = "/qqq_trade.txt"
    fullpath += filename
    return fullpath
def geterrorDescription(module_name, error_code, error_description):
    ret = {"module_name":module_name,\
           "error_code": error_code, \
           "error_description":error_description}
    return ret
if __name__ == "__main__":
    d = GetDataFileDirectory()
    fp = GetDataFileFullPath("qqq", "12/01/2014")
    fp_abs = os.path.abspath(fp)
    try:
        f = open(fp, "r")
        #f = open(fp_abs, "r")
    except IOError, e:
        print(e)
    except OSError, e:
        pass

    print(d)