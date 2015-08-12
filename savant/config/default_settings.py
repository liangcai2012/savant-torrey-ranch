import os
base_dir = "/".join(os.path.realpath(__file__).split("/")[:-3])
tmp_dir = os.path.join(base_dir, "tmp")

DEBUG = False

LOG_DIR = os.path.join(tmp_dir, "log")
DOWNLOAD_DIR = os.path.join(tmp_dir, "data")
DATABASE_URI = "sqlite:///" + os.path.join(tmp_dir, "savant.db")

FETCHER_HOST = 'localhost'
FETCHER_PORT = 8080

AT_HOSTNAME = 'activetick1.activetick.com'
AT_PORT = 443
AT_GUID = '80af4953bb7f4dcf85523ad332161eff'
AT_USER = 'liangcai'
AT_PASSWORD = 'S@^@nt932456'
