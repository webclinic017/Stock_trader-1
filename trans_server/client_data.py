import time
import threading
from currency import Currency
import threading
import requests
import os
from dotenv import load_dotenv
load_dotenv()
user_db_host = os.environ.get("user_db_host")
user_db_port = int(os.environ.get("user_db_port"))

class UserUrls:
	AUTHENTICATE = "authenticate"
	CHECK_SESSION = "check_session"
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
	CLEAR_OLD_COMMANDS = "clear_old_commands"

class ClientData:
	# Could be extended to load users on init
	def __init__(self, server_name, protocol):
		self.user_db_host = user_db_host
		self.user_db_port = user_db_port
		self._server_name = server_name
		self.lock = threading.Lock()
		self.user_server_url = f"{protocol}://{self.user_db_host}:{self.user_db_port}"

	def authenticate(self, username, password):
		data = {"username": username, "password": password}
		response = self.post_to_model(UserUrls.AUTHENTICATE, data)
		return response

	def check_session(self, username, session):
		data = {"username": username, "session": session}
		response = self.post_to_model(UserUrls.CHECK_SESSION, data)
		return response

	def get_current_funds(self, username):
		data = requests.get(f"{self.user_server_url}/{UserUrls.CURRENT_FUNDS}/{username}").json()
		return Currency(data["dollars"]) + Currency(int(data["cents"]) / 100)

	def post_to_model(self, endpoint, data_dict):
		return requests.post(f"{self.user_server_url}/{endpoint}", json=data_dict).json()

	def new_user(self, username):
		# acc -> float, account balance
		# stk -> dictionary[symbol] -> int, number of stocks of "symbol" owned
		# buy -> stack of pending buys 
		# sel -> stack of pending sells
		
		assert type(username) == str
		return self.post_to_model(UserUrls.CREATE_NEW_USER, {"username": username})

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
		return account

	def get_stock_held(self, user, stock_symbol):
		stocks_held = int(requests.get(f"{self.user_server_url}/{UserUrls.GET_STOCKS_HELD}/{user}/{stock_symbol}").json())
		return stocks_held

	def add_money(self, user, amount):
		try:
			assert type(user) == str
			amount = Currency(amount)
			self.post_to_model(UserUrls.ADD_FUNDS, {"username": user, "dollars": amount.dollars, "cents": amount.cents})
		except KeyError:
			self.new_user(user)

		return True

	def commit_buy(self, username, stock_symbol, price, buy_amount):
		return self.post_to_model(
			UserUrls.COMMIT_BUY, 
			{
				"username": username,
				"stock_symbol": stock_symbol, 
				"stock_price_dollars": price.dollars, 
				"stock_price_cents": price.cents, 
				"dollars_delta": buy_amount.dollars, 
				"cents_delta": buy_amount.cents
			}
		)

	def commit_sell(self, username, stock_symbol, price, count):
		total = price * count
		stock_price = Currency(price)
		cost = stock_price * count
		return self.post_to_model(
			UserUrls.COMMIT_SELL, 
			{
				"username": username,
				"stock_symbol": stock_symbol, 
				"stock_price_dollars": stock_price.dollars, 
				"stock_price_cents": stock_price.cents, 
				"dollars_delta": cost.dollars, 
				"cents_delta": cost.cents
			}
		)

	##### Buy and Sell Commands #####
	def clear_old(self, user, command, current_time):
		requests.post(f"{self.user_server_url}/{UserUrls.CLEAR_OLD_COMMANDS}", json={"username": user, "command": command, "current_time": current_time})

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
		#self.clear_old(user, key, time.time())
		self.lock.acquire()
		data = {}
		try:
			data = requests.get(f"{self.user_server_url}/{UserUrls.POP_COMMAND}/{user}/{key}").json()
		finally:
			self.lock.release()
		return data