from . import sopen
from . import sclose
import sys

def getMFunctionByName(moduleName, methodName):
    m = __import__ (moduleName)
    fields = methodName.split(".")
    r = dir(m)
    print(r)
    if(len(fields) == 1):
        method = getattr(m,fields[0])
    elif(len(fields) == 2):
        module = getattr(m,fields[0])
        method = getattr(module,fields[1])
        pass
    else:
        raise Exception("un supported")


    if not method:
        raise Exception("Method %s not implemented" % methodName)
    return method


def getFunctionByName(methodName):
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(methodName)
    #method = possibles.get(method_name)()
    if not method:
         raise Exception("Method %s not implemented" % method_name)
    return method
def ShowSysInfo():
    print(sys.version )
    i = 0
    for p in sys.path:
        print(i, p)
        i = i +1
