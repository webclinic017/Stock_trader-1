import time
import threading
from currency import Currency
import threading
import requests

class UserUrls:
		CURRENT_FUNDS = "current_funds"
		COMMIT_BUY = "commit_buy"
		COMMIT_SELL = "commit_sell"
		ADD_FUNDS = "add_funds"
		CREATE_NEW_USER = "create_new_user"
		SET_BUY_TRIGGER = "set_buy_trigger"
		SET_SELL_TRIGGER = "set_sell_trigger"
		GET_STOCKS_HELD = "get_stocks_held"
		PUSH_COMMAND = "push_command"
		POP_COMMAND = "pop_command"

class ClientData:

	# Could be extended to load users on init
	def __init__(self, server_name, protocol, user_db_host, user_db_port):
		self._server_name = server_name
		self.lock = threading.Lock()
		self.user_server_url = f"{protocol}://{user_db_host}:{user_db_port}"
		self.cli_data = {"buy": [], "sel": []}

	def get_current_funds(self, username):
		data = requests.get(f"{self.user_server_url}/{UserUrls.CURRENT_FUNDS}/{username}").json()
		return Currency(data["dollars"]) + Currency(int(data["cents"]) / 100)

	def persist(self, endpoint, data_dict):
		return requests.post(f"{self.user_server_url}/{endpoint}", json=data_dict).json()

	def new_user(self, username):
		# acc -> float, account balance
		# stk -> dictionary[symbol] -> int, number of stocks of "symbol" owned
		# buy -> stack of pending buys 
		# sel -> stack of pending sells
		
		assert type(username) == str
		return self.persist(UserUrls.CREATE_NEW_USER, {"username": username})

	def get_user(self, username):
		assert type(username) == str
		response = requests.get(f"{self.user_server_url}/get_user/{username}").json()
		return response

	##### Account Commands #####
	def check_money(self, user):
		try:
			account = self.get_current_funds(user)
		except KeyError:

			response = self.new_user(user)

			account = Currency(0.0)
		print(f"Lock released: check_money |{user}")
		return account

	def get_stock_held(self, user, stock_symbol):
		return requests.get(f"{self.user_server_url}/{UserUrls.GET_STOCKS_HELD}/{user}/{stock_symbol}")

	def add_money(self, user, amount):
		try:
			assert type(user) == str
			amount = Currency(amount)
			self.persist(UserUrls.ADD_FUNDS, {"username": user, "dollars": amount.dollars, "cents": amount.cents})
		except KeyError:
			self.new_user(user)

		return True

	def commit_buy(self, username, stock_symbol, price, count):
		total = price * count
		stock_price = Currency(price)
		cost = stock_price * count

		#TODO: temporarily keep stack of buy commands in memory
		self.cli_data[username]
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

	##### Buy and Sell Commands #####
	def clear_old(self, user, key, curr):
		filtered = []
		command_stack = self.cli_data[user][key]
		self.lock.acquire()
		try:
			for cmd in command_stack:
				if curr - cmd[2] >= 60:
					if key == "buy":
						self.add_money(user, cmd[1])
					else:
						self.add_stock(user, cmd[0], cmd[1][1])
				else:
					filtered.append(cmd)
			self.cli_data[user][key] = filtered
		finally:
			self.lock.release()

	def push(self, user, symbol, amount, command):
		self.lock.acquire()
		try:
			currencyAmount = Currency(amount)
			data = {
				"username": user, 
				"stock_symbol": symbol, 
				"dollars": currencyAmount.dollars, 
				"cents": currencyAmount.cents, 
				"command": command, 
				"timestamp": time.time()
			}
			requests.post(f"{self.user_server_url}/{UserUrls.PUSH_COMMAND}", json=data)
		finally:
			self.lock.release()

	def pop(self, user, key):
		self.clear_old(user, key, time.time())
		self.lock.acquire()
		record = ()  # not sure about this
		try:
			record = requests.get(f"{self.user_server_url}/{user}/{UserUrls.POP_COMMAND}")
		finally:
			self.lock.release()
		return record
