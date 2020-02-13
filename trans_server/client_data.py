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

	def new_user(self, user, amount=0.0, stock={}, buys=[], sells=[]):
		# acc -> float, account balance
		# stk -> dictionary[symbol] -> int, number of stocks of "symbol" owned
		# buy -> stack of pending buys 
		# sel -> stack of pending sells
		self.cli_data[user] = {"acc": amount, "stk": stock, "buy": buys, "sel": sells}
		return self.cli_data[user]

	def get_user_account(self, user):
		print(f"Lock Wait: get_user_account |{user}")
		self.lock.acquire()
		print(f"Lock acquired: get_user_account |{user}")
		try:
			account = self.cli_data[user]
		except KeyError:
			account = self.new_user(user=user)
		self.lock.release()
		print(f"Lock released: get_user_account |{user}")
		return account

	##### Account Commands #####
	def check_money(self, user):
		funds = -1.0  # TODO: What is this var set here for? I believe except handles it properly
		print(f"Lock Wait: check_money |{user}")
		self.lock.acquire()
		print(f"Lock acquired: check_money |{user}")
		try:
			funds = self.cli_data[user]["acc"]
		except KeyError:
			self.new_user(user=user)
			funds = 0.0
		self.lock.release()
		print(f"Lock released: check_money |{user}")
		return funds

	def add_money(self, user, amount):
		print(f"Lock Wait: add_money |{user}|{amount}")
		self.lock.acquire()
		print(f"Lock acquired: add_money |{user}|{amount}")
		try:
			amount = float(amount)
			self.cli_data[user]["acc"] += round(amount, 2)
		except KeyError:
			self.new_user(user=user, amount=amount)
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

	def rem_money(self, user, amount):
		succeeded = False
		self.clear_old(user, "buy", time.time())
		print(f"Lock Wait: rem_money |{user}|{amount}")
		self.lock.acquire()
		print(f"Lock acquired: rem_money |{user}|{amount}")
		try:
			amount = float(amount)
			if self.cli_data[user]["acc"] >= amount:
				self.cli_data[user]["acc"] -= round(amount, 2)
				succeeded = True
		except KeyError:
			self.new_user(user=user)
		self.lock.release()
		print(f"Lock released: rem_money |{user}|{amount}")

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
	def get_stock_held(self, user, symbol):
		print(f"Lock Wait: get_stock_held |{user}|{symbol}")
		self.lock.acquire()
		print(f"Lock acquired: get_stock_held |{user}|{symbol}")
		num_shares = 0
		try:
			stocks = self.cli_data[user]["stk"]
			try:
				num_shares = stocks[symbol]
			except KeyError:
				pass
		except KeyError:
			self.new_user(user=user)
		self.lock.release()
		print(f"Lock released: get_stock_held |{user}|{symbol}")
		return num_shares

	def add_stock(self, user, stock, count):
		print(f"Lock Wait: add_stock |{user}|{stock}|{count}")
		self.lock.acquire()
		print(f"Lock acquired: add_stock |{user}|{stock}|{count}")
		try:
			count = int(count)
			stocks = self.cli_data[user]["stk"]
			try:
				stocks[stock] += count
			except KeyError:
				stocks[stock] = count
		except KeyError:
			self.new_user(user=user, stock={stock: count})
		self.lock.release()
		print(f"Lock released: add_stock |{user}|{stock}|{count}")

		# DEBUG
		print("ADD STOCK: " + user + "\t" + str(self.cli_data[user]["stk"]) + "\t" + str(True))

		return True

	def rem_stock(self, user, stock, count):
		succeeded = False
		self.clear_old(user, "sel", time.time())
		print(f"Lock Wait: rem_stock |{user}|{stock}|{count}")
		self.lock.acquire()
		print(f"Lock acquired: rem_stock |{user}|{stock}|{count}")
		try:
			count = int(count)
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
			self.new_user(user=user)
		self.lock.release()
		print(f"Lock released: rem_stock |{user}|{stock}|{count}")

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
		print(f"Lock Wait: push |{user}|{symbol}|{amount}|{key}")
		self.lock.acquire()  # TODO: Can we have have user specific locks instead of locking all client data?
		print(f"Lock acquired: push |{user}|{symbol}|{amount}|{key}")
		# TR-Remove any pre-existing buy/sell order for the same stock for the given user
		filtered_client_data = [order for order in self.cli_data[user][key] if order[0] != symbol]
		self.cli_data[user][key] = filtered_client_data
		self.cli_data[user][key].append((symbol, amount, time.time()))
		self.lock.release()
		print(f"Lock released: push |{user}|{symbol}|{amount}|{key}")

	def pop(self, user, key):
		self.clear_old(user, key, time.time())
		print(f"Lock Wait: pop |{user}|{key}")
		self.lock.acquire()
		print(f"Lock acquired: pop |{user}|{key}")
		try:
			record = self.cli_data[user][key].pop()
		except Exception:
			self.lock.release()
			raise Exception
		self.lock.release()
		print(f"Lock released: pop |{user}|{key}")
		return record
