import socket
import time
import threading

class QuoteCache:
	def __init__(self, addr, port):
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((addr, port))
		# Simulating DB with dictionary
		self.quotes = dict()
		self.lock = threading.Lock()

	def requote(self, symbol, user):
		# REAL
		#self.conn.send(str.encode(symbol + ", " + user))
		#data = self.conn.recv(1024).decode().split(",")

		#STUB
		data = ["20.87", symbol, user, time.time(), "QWERTYUIOP"]

		data[0] = float(data[0])
		qtm = time.time()
		self.quotes[symbol] = (qtm, data,)
			
		return data

	def quote(self, symbol, user):
		val = []
		self.lock.acquire()
		try:
			q = self.quotes[symbol]
			if q[0] - time.time() >= 60:
				val = self.requote(symbol, user)
			else:
				val = q[1]
		except KeyError:
			val = self.requote(symbol, user)
		print(str(val))
		self.lock.release()
		return val
