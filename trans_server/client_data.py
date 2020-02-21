import time
import threading
from currency import Currency
from audit_logger.AuditLogBuilder import AuditLogBuilder
from audit_logger.AuditCommandType import AuditCommandType

import requests

# Surrogate for client database
# Provides API for actions on client records

class ClientData:
	class UserUrls():
		CURRENT_FUNDS = "current_funds"
		COMMIT_BUY = "commit_buy"
		COMMIT_SELL = "commit_sell"
		ADD_FUNDS = "add_funds"
		CREATE_NEW_USER = "create_new_user"
		SET_BUY_TRIGGER = "set_buy_trigger"
		SET_SELL_TRIGGER = "set_sell_trigger"
		GET_STOCKS_HELD = "get_stocks_held"

	_commandType = AuditCommandType.accountTransaction

	# Could be extended to load users on init
	def __init__(self, server_name, protocol, user_db_host, user_db_port):
		self._server_name = server_name
		self.lock = threading.Lock()
		self.user_server_url = f"{protocol}://{user_db_host}/{user_db_port}"

	def get_current_funds(self, username):
		data = requests.get(f"{self.user_server_url}/{UserUrls.CURRENT_FUNDS}")["data"]
		return Currency(data["dollars"]) + Currency(data["cents"] / 100)

	def persist(self, endpoint, data_dict):
		return requests.post(f"{user_server_url}/{endpoint}", json=data_dict)

	def new_user(self, username):
		# acc -> float, account balance
		# stk -> dictionary[symbol] -> int, number of stocks of "symbol" owned
		# buy -> stack of pending buys 
		# sel -> stack of pending sells
		
		#self.cli_data[user] = {"acc": amount, "stk": stock, "buy": buys, "sel": sells}
		assert type(username) == str
		return self.persist(UserUrls.CREATE_NEW_USER, {"username": username})

	##### Account Commands #####
	def check_money(self, user):
		account = -1.0  # TODO: What is this var set here for? I believe except handles it properly
		print(f"Lock Wait: check_money |{user}")
		self.lock.acquire()
		print(f"Lock acquired: check_money |{user}")
		try:
			account = self.get_current_funds(user)
		except KeyError:
			response = self.new_user(user)
			account = Currency(response["data"]["dollars"]) + Currency(response["data"]["cents"] / 100)
		finally:
			self.lock.release()
		print(f"Lock released: check_money |{user}")
		return account

	def get_stock_held(self, user, stock_symbol):
		return requests.get(f"{self.user_server_url}/{UserUrls.GET_STOCKS_HELD}/{user}/{stock_symbol}")

	def add_money(self, user, amount):
		print(f"Lock Wait: add_money |{user}|{amount}")
		self.lock.acquire()
		print(f"Lock acquired: add_money |{user}|{amount}")
		try:
			amount = Currency(amount)
			dollars= amount.dollars
			cents = amount.cents
			assert type(user) == str
			self.persist(UserUrls.ADD_FUNDS, {"username": user, "dollars": dollars, "cents": cents})
		except KeyError:
			self.new_user(user)
		finally:
			self.lock.release()
		print(f"Lock released: add_money |{user}|{amount}")

		# DEBUG
		print("ADD MONEY: " + user + "\t" + str(self.cli_data[user]["acc"]) + "\t" + str(True))
		AuditLogBuilder("ADD", self._server_name, self._commandType).build({
			"server": self._server_name,
			"userid": user,
			"action": "ADD",
			"amount": amount 
		}).send()

		return True

	def commit_buy(self, username, stock_symbol, price, count):
		total = price * count
		stock_price = Currency(price)
		cost = stock_price * count
		self.persist(
			UserUrls.COMMIT_BUY, 
			{
				"username": username,
				"stock_symbol": stock_symbol, 
				"stock_dollars": stock_price.dollars, 
				"stock_cents": stock_price.cents, 
				"dollars_delta": cost.dollars, 
				"cents_delta": cost.cents
			}
		)

	def commit_sell(self, username, stock_symbol, price, count):
		total = price * count
		stock_price = Currency(price)
		cost = stock_price * count
		self.persist(
			UserUrls.COMMIT_SELL, 
			{
				"username": username,
				"stock_symbol": stock_symbol, 
				"stock_dollars": stock_price.dollars, 
				"stock_cents": stock_price.cents, 
				"dollars_delta": cost.dollars, 
				"cents_delta": cost.cents
			}
		)

	#def rem_money(self, user, amount):
	#	succeeded = False
	#	self.clear_old(user, "buy", time.time())
	#	print(f"Lock Wait: rem_money |{user}|{amount}")
	#	self.lock.acquire()
	#	print(f"Lock acquired: rem_money |{user}|{amount}")
	#	try:
	#		amount = float(amount)
	#		funds = self.get_current_funds(user)
	#		if funds >= amount:
	#			self.persist(UserUrls.ADD_FUNDS)
	#			succeeded = True
	#	except KeyError:
	#		self.new_user(user)
	#	finally:
	#		self.lock.release()
	#	print(f"Lock released: rem_money |{user}|{amount}")
#
	#	# DEBUG
	#	print("REM MONEY: " + user + "\t" + str(self.cli_data[user]["acc"]) + "\t" + str(succeeded))
	#	AuditLogBuilder("REMOVE", self._server_name, self._commandType).build({
	#		"server": self._server_name,
	#		"userid": user,
	#		"action": "REMOVE",
	#		"amount": amount 
	#	}).send()
	#	return succeeded

	##### Portfolio Commands #####
#	def add_stock(self, user, stock, count):
#		print(f"Lock Wait: add_stock |{user}|{stock}|{count}")
#		self.lock.acquire()
#		print(f"Lock acquired: add_stock |{user}|{stock}|{count}")
#		try:
#			count = int(count)
#			stocks = self.cli_data[user]["stk"]
#			try:
#				stocks[stock] += count
#			except KeyError:
#				stocks[stock] = count
#		except KeyError:
#			self.new_user(user)
#		finally:
#			self.lock.release()
#		print(f"Lock released: add_stock |{user}|{stock}|{count}")
#
#		# DEBUG
#		print("ADD STOCK: " + user + "\t" + str(self.cli_data[user]["stk"]) + "\t" + str(True))
#
#		return True
#
#	def rem_stock(self, user, stock, count):
#		succeeded = False
#		self.clear_old(user, "sel", time.time())
#		print(f"Lock Wait: rem_stock |{user}|{stock}|{count}")
#		self.lock.acquire()
#		print(f"Lock acquired: rem_stock |{user}|{stock}|{count}")
#		try:
#			count = int(count)
#			stocks = self.cli_data[user]["stk"]
#			try:
#				if stocks[stock] >= count:
#					stocks[stock] -= count
#					succeeded = True
#					if stocks[stock] <= 0:
#						self.cli_data[user]["stk"].pop(stock)
#			except KeyError:
#				stocks[stock] = 0
#		except KeyError:
#			self.new_user(user)
#		finally:
#			self.lock.release()
#		print(f"Lock released: rem_stock |{user}|{stock}|{count}")
#
#		# DEBUG
#		print("REM STOCK: " + user + "\t" + str(self.cli_data[user]["stk"]) + "\t" + str(succeeded))
#
#		return succeeded

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
		print(f"Lock Wait: push |{user}|{symbol}|{amount}|{key}")
		self.lock.acquire()
		print(f"Lock acquired: push |{user}|{symbol}|{amount}|{key}")
		self.cli_data[user][key].append((symbol, amount, time.time()))
		self.lock.release()
		print(f"Lock released: push |{user}|{symbol}|{amount}|{key}")

	def pop(self, user, key):
		self.clear_old(user, key, time.time())
		print(f"Lock Wait: pop |{user}|{key}")
		self.lock.acquire()
		print(f"Lock acquired: pop |{user}|{key}")
		record = ()  # not sure about this
		try:
			record = self.cli_data[user][key].pop()
		finally:
			self.lock.release()
		print(f"Lock released: pop |{user}|{key}")
		return record
