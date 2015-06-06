import os, os.path, sys
import logging
import datetime

from savant.config import settings

class SavantLogger:
    MODULES = ["streamer","viewer","fetcher","db"]
    DEFAULT_FORMAT = "%(asctime)-15s %(name)s %(levelname)s %(message)s"

    def __init__(self,mod,log_format=None,level=None):
        if mod not in self.MODULES:
            raise Exception("Module %s not supported" % mod)
        self.mod = mod
        self.log_format = log_format if log_format else self.DEFAULT_FORMAT
        self.level = level
        self.config()

    def config(self):
        self.base_dir = os.path.join(settings.OUTPUT_DIR, "log", self.mod)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        date = datetime.date.today().strftime("%Y%m%d")
        self.log_file = os.path.join(self.base_dir,"%s.python.log" % date)
        self.logger = logging.getLogger(self.mod)
        self.hdlr = logging.FileHandler(self.log_file,mode="a")
        self.formatter = logging.Formatter(self.log_format)
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        if self.level:
            self.logger.setLevel(getattr(logging, self.level.upper()))

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


def getLogger(mod,log_format=None,level=None):
    return SavantLogger(mod,log_format=log_format,level=level)


if __name__ == "__main__":
    logger = getLogger("fetcher")
    logger.error("test")
