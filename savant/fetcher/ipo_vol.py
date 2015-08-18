import sqlite3 as lite
import gzip
import csv
import collections
db_path = '../db/savant.db'
data_root_path = "../../out/data"


def GetCompanyId(symbol):


    sql = "SELECT * FROM COMPANY where symbol =\'" +symbol +"\';"
    record = get_record_bySQL(sql)
    compandid = record[0]

    return compandid

def get_record_bySQL(sql):
    con = lite.connect(db_path)

    cur = con.cursor()
    with con:
        cur.execute(sql)
        rows = cur.fetchall()

    return rows[0]

def getipo_record(company_id):
    sql = "SELECT * FROM historical_ipo where company_id = " + str(company_id) + ";"
    record = get_record_bySQL(sql)
    #print(record)
    return record


def getTradeData(ipodate, symbol):
    ipo_first_tick_vol = 0

    # remove "-"
    ipodata = ipodate.replace("-", "")
    filename= symbol+"_markethours.csv.gz";
    full_path = data_root_path +"/" + ipodata+ "/"+ filename

    #filepath = "/run/media/zhiqinc/doc-drv/savant-torrey-ranch/0715/out/data/20100805/GMAN_aftermarket.csv.gz"
    archive = gzip.open(full_path, 'r')
    data = archive.read()
    #print(line1)
    data_rows = data.split("\n")
    for dr in data_rows:
        fields = dr.split(",")
        if fields[5] == "0":
            ipo_first_tick_vol = int(fields[3])
            break;
    print(ipo_first_tick_vol)
    return ipo_first_tick_vol
def get_ipo_vol_info(symbol):

    id =GetCompanyId(symbol)
    ipoinfo = getipo_record(id)
    ipodate = ipoinfo[1]
    ipo_shares = int(ipoinfo[4])
    ipo_first_tick_vol = getTradeData(ipodate, symbol)
    ft_vol_2_floating_rate = float(ipo_first_tick_vol)/ ipo_shares
    print(ipo_first_tick_vol,ft_vol_2_floating_rate)
    ret = collections.OrderedDict()
    ret["symbol"]=symbol
    ret["ipo_shares"]=ipo_shares
    ret["first tick vol"]=ipo_first_tick_vol
    ret["first_tick_vol2ipo_shares"]=ft_vol_2_floating_rate

    return ret
def save2cvs(file_name, my_dict, append):
    if append == False:
        with open(file_name, 'wb') as f:  # Just use 'w' mode in 3.x
            w = csv.DictWriter(f, my_dict.keys())
            w.writeheader()
            w.writerow(my_dict)
    else:
         with open(file_name, 'a+') as f:
            w = csv.DictWriter(f, my_dict.keys())
            w.writerow(my_dict)
    #w.writerow(my_dict2)
# todo: handle the symbol that ipo data is not available
def generate_ipo_first_tick_vol_report(symbols):
    index = 0
    for s in symbols:
        ret = get_ipo_vol_info(s)
        if index == 0:
            append2file = False
        else:
            append2file = True

        save2cvs("output.csv", ret, append2file)
        index = index+ 1

def test1():
    symbol = "KANG"
    ret = get_ipo_vol_info(symbol)
    save2cvs("output.csv", ret, False)
    save2cvs("output.csv", ret, True)
    print ret
def main():
    #symbols = ["KANG", "AMCF"]
    symbols = ["KANG","AMBA"]
    generate_ipo_first_tick_vol_report(symbols)

main()


