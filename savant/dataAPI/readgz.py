import gzip
import io
#filepath = "/run/media/zhiqinc/doc-drv/savant-torrey-ranch/0715/out/data/20150805/RUN_markethours.csv.gz"
filepath = "../../out/data/20150805/BETR_markethours.csv.gz"
class Reader_gz:
    def __init__(self):
         self.__str_io = None
    def open(self, ilepath):
        archive = gzip.open(filepath, 'r')
        data = archive.read()
        data = unicode(data)
        self.__str_io = io.StringIO(data)
        archive.close()
    def readline(self):
        dl = self.__str_io.readline()
        return dl
def main():
    reader = Reader_gz()
    reader.open(filepath)
    lc = 0
    while True:
        dl = reader.readline()
        if len(dl)==0:
            print("lineread", "Done")
            break
        print lc, dl
        lc = lc +1

if __name__ == "__main__":
    main()

