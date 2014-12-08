from Base import Base

class Simple(Base):

    def __init__(self):
        Base.__init__(self)
        self.symbols = ["QQQ"]

    def run(self):
        print "Start running Simple Strategy"
        print "Symbols: " + ",".join(self.symbols)

