import os, os.path, sys
import socket
import json
import argparse

from savant.config import settings

class FetcherCaller:

    def __init__(self,json_request):
        self.request = json_request+"\n"
        self.connect()
        self.send_request()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((settings.FETCHER_HOST, int(settings.FETCHER_PORT)))

    def send_request(self):
        print self.request
        self.socket.sendall(self.request)
        resp = self.socket.recv(1024)
        print "Response:",resp
        self.socket.close()

def get_data(args):
    cmd = "get"
    symbol = args.symbol
    date = args.date
    request = {"command":cmd,"symbol":symbol,"date":date}
    json_request = json.dumps(request)
    caller = FetcherCaller(json_request)    

def check_status(args):
    cmd = "check"
    request = {"command":cmd}
    json_request = json.dumps(request)
    caller = FetcherCaller(json_request)

def cancel(args):
    cmd = "cancel"
    request = {"command":cmd}
    json_request = json.dumps(request)
    caller = FetcherCaller(json_request)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands")
    
    psr_get = subparsers.add_parser("get",help="get tick data")
    psr_get.add_argument("symbol",help="stock symbol")
    psr_get.add_argument("date",help="date")
    psr_get.set_defaults(func=get_data)

    psr_check = subparsers.add_parser("check",help="check fetcher status")
    psr_check.set_defaults(func=check_status)    

    psr_cancel = subparsers.add_parser("cancel",help="cancel fetching")
    psr_cancel.set_defaults(func=cancel)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
