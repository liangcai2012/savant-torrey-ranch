import os, os.path, sys
import logging
import datetime

class Logger:
    BASE_DIR = "/".join(os.path.realpath(__file__).split("/")[:-5]+["savant/log"])
    MODULES = ["streamer","viewer","fetcher"]
    DEFAULT_FORMAT = "%(asctime)-15s %(name)s %(levelname)s %(message)s"

    def __init__(self,mod,log_format=None,level=None):
        if mod not in self.MODULES:
            raise Exception("Module %s not supported" % mod)
        date = datetime.date.today().strftime("%y%m%d")
        self.log_file = os.path.join(self.BASE_DIR,"%s/%s.log" % (mod,date))
        if not log_format:
            self.log_format = self.DEFAULT_FORMAT
        self.logger = logging.getLogger(mod)
        self.hdlr = logging.FileHandler(self.log_file)
        self.formatter = logging.Formatter(self.log_format)
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        if level:
            self.logger.setLevel(getattr(logging,level.upper()))

    def info(self,message):
        self.logger.info(message)

    def error(self,message):
        self.logger.error(message)

    def warning(self,message):
        self.logger.warning(message)

    def debug(self,message):
        self.logger.debug(message)

    def setFormat(self,format_string):
        self.log_format = format_string
        self.formatter = logging.Formatter(format_string)
        self.hdlr.setFormatter(self.formatter)

    def setLevel(self,level):
        self.logger.setLevel(level)

if __name__ == "__main__":
    logger = Logger("fetcher")
    logger.error("test")
