import os, os.path, sys
import time
import socket
import json
import argparse

from savant.config import settings

class StreamerCaller:

	def __init__(self):
		self.connected = False;

	def send_request(self, json_request):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((settings.STREAMER_HOST, int(settings.STREAMER_PORT)))
		self.socket.sendall(json_request+'\n')
		resp = ""
		part = None
		while part != "":
			part = self.socket.recv(4096)
			resp+=part
		self.socket.close()
		return resp

	def subscribe(self, clientname, symlist):
		request = {"request": {\
					"command":"subscribe",\
					"client":clientname,\
					"symlist":symlist\
					}\
				   }
		return self.send_request(json.dumps(request))    

	def unsubscribe(self, clientname):
		request = {"request": {\
					"command":"unsubscribe",\
					"client":clientname,\
					}\
				   }
		return self.send_request(json.dumps(request))    

	def update(self, clientname, interval, ma_mask=""):
		request = {"request": {\
					"command":"update",\
					"client":clientname,\
					"interval":interval,\
					"bar_mask":"0x11111",\
					"ma_mask":ma_mask,\
					}\
				   }
		return self.send_request(json.dumps(request))    

def getStreamerCaller():
	return StreamerCaller()

