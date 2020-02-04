import time
import threading
from audit_logger.AuditLogBuilder import AuditLogBuilder
from audit_logger.AuditCommandType import AuditCommandType

# Surrogate for client database
# Provides API for actions on client records

class ClientData:
	_commandType = AuditCommandType.accountTransaction

	# Could be extended to load users on init
	def __init__(self, server_name):
		self._server_name = server_name
		self.lock = threading.Lock()
		self.cli_data = dict()

	def new_user(self, user, amount, stock, buys, sells):
		# acc -> float, account balance
		# stk -> dictionary[symbol] -> int, number of stocks of "symbol" owned
		# buy -> stack of pending buys 
		# sel -> stack of pending sells
		self.cli_data[user] = {"acc": amount, "stk": stock, "buy": buys, "sel": sells}

	##### Account Commands #####
	def check_money(self, user):
		account = -1.0
		self.lock.acquire()
		try:
			account = self.cli_data[user]["acc"]
		except KeyError:
			self.new_user(user, 0.0, dict(), [], [])
			account = 0.0
		self.lock.release()
		return account

	def add_money(self, user, amount):
		self.lock.acquire()
		try:
			amount = float(amount)
			self.cli_data[user]["acc"] += amount
		except KeyError:
			self.new_user(user, amount, dict(), [], [])
		self.lock.release()

		# DEBUG
		print("ADD MONEY: " + user + "\t" + str(self.cli_data[user]["acc"]) + "\t" + str(True))
		AuditLogBuilder("ADD", self._server_name, self._commandType).build({
			"server": self._server_name,
			"userid": user,
			"action": "ADD",
			"amount": amount 
		}).send()

		return True

	def rem_money(self, user, amount):
		succeeded = False
		self.lock.acquire()
		try:
			amount = float(amount)
			self.clear_old(user, "buy", time.time())
			if self.cli_data[user]["acc"] >= amount:
				self.cli_data[user]["acc"] -= amount
				succeeded = True
		except KeyError:
			self.new_user(user, 0.0, dict(), [], [])
		self.lock.release()

		# DEBUG
		print("REM MONEY: " + user + "\t" + str(self.cli_data[user]["acc"]) + "\t" + str(succeeded))
		AuditLogBuilder("REMOVE", self._server_name, self._commandType).build({
			"server": self._server_name,
			"userid": user,
			"action": "REMOVE",
			"amount": amount 
		}).send()
		return succeeded

	##### Portfolio Commands #####
	def add_stock(self, user, stock, count):
		self.lock.acquire()
		try:
			count = int(count)
			stocks = self.cli_data[user]["stk"]
			try:
				stocks[stock] += count
			except KeyError:
				stocks[stock] = count
		except KeyError:
			self.new_user(user, 0.0, {stock: count}, [], [])
		self.lock.release()

		# DEBUG
		print("ADD STOCK: " + user + "\t" + str(self.cli_data[user]["stk"]) + "\t" + str(True))

		return True

	def rem_stock(self, user, stock, count):
		succeeded = False
		self.lock.acquire()
		try:
			count = int(count)
			self.clear_old(user, "sel", time.time())
			stocks = self.cli_data[user]["stk"]
			try:
				if stocks[stock] >= count:
					stocks[stock] -= count
					succeeded = True
					if stocks[stock] <= 0:
						self.cli_data[user]["stk"].pop(stock)
			except KeyError:
				stocks[stock] = 0
		except KeyError:
			self.new_user(user, 0.0, dict(), [], [])
		self.lock.release()

		# DEBUG
		print("REM STOCK: " + user + "\t" + str(self.cli_data[user]["stk"]) + "\t" + str(succeeded))

		return succeeded

	##### Buy and Sell Commands #####
	def clear_old(self, user, key, curr):
		filtered = []
		command_stack = self.cli_data[user][key]

		for cmd in command_stack:
			if curr - cmd[2] >= 60:
				if key == "buy":
					self.add_money(user, cmd[1])
				else:
					self.add_stock(user, cmd[0], cmd[1][1])
			else:
				filtered.append(cmd)
		self.cli_data[user][key] = filtered

	def push(self, user, symbol, amount, key):
		self.lock.acquire()
		self.cli_data[user][key].append((symbol, amount, time.time()))
		self.lock.release()

	def pop(self, user, key):
		self.clear_old(user, key, time.time())
		self.lock.acquire()
		record = ()  # not sure about this
		try:
			record = self.cli_data[user][key].pop()
		except Exception:
			self.lock.release()
			raise Exception
		self.lock.release()
		return record
