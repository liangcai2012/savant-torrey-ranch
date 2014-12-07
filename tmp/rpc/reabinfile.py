import locale
def FormatInt(v):
    locale.setlocale(locale.LC_ALL, 'en_US')
    r = locale.format("%d", v, grouping=True)
    print(r)
    return r
def showinfo(obj):
    t = type(obj)
    print(t)
fileName="C:\\Users\\KCai\\Downloads\\jdk-8u25-windows-x64.exe"

def GetFileContent(fileName):
    with open(fileName, mode='rb') as file: # b is important -> binary
        fileContent = file.read()
        size = len(fileContent)
        FormatInt(size)
        print(size)
        showinfo(fileContent)
    return fileContent
def getBigFileData():
    #fileName="/home/zhiqincz/Downloads/eclipse-java-luna-SR1-linux-gtk-x86_64.tar.gz"
    #fileName="/home/zhiqincz/Downloads/get-pip.py"
    fileName="/media/new_disk/downloads/Python-3.3.4.tgz"
    data = GetFileContent(fileName)
    return data
