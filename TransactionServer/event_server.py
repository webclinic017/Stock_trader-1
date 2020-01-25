import time
import threading
import json

class QuoteThread(threading.Thread):
	def __init__(self, cli_data, cache, ver, user, symbol, amount, price):
		super().__init__()
		self.ver = ver
		self.cli_data = cli_data
		self.cache = cache
		self.user = user
		self.symbol = symbol
		self.amount = amount
		self.price = price
		self.stopevent = threading.Event()

	def run(self):
		while not self.stopevent.isSet():
			quote = self.cache.quote(self.symbol, self.user)[0]
			if (self.ver == "buy" and quote <= self.price):
				count = int(self.amount / quote)
				delta = self.amount - (count * quote)
				# Add bought stock to portfolio
				self.cli_data.add_stock(self.user, self.symbol, count)
				# Add delta of transaction back to balance
				self.cli_data.add_money(self.user, delta)
				break
			elif (self.ver == "sel" and quote >= self.price):
				value = quote * self.amount
				# Add sell amount to balance
				self.cli_data.add_money(self.user, value)
				break
			self.stopevent.wait(60.0)
	
	def join(self):
		self.stopevent.set()
		threading.Thread.join(self, None)

class EventServer:
	def __init__(self):
		self.timers = {"buy":{},"sel":{}}

	def give_hooks(self, cli_data, cache):
		self.cache = cache
		self.cli_data = cli_data

	# TransactionServer must deducted the amount returned from account balance
	def register(self, ver, user, symbol, amount):
		succeeded = False
		try:
			curr = self.timers[ver][user]
			try:
				# Buy trigger already running, must cancel before setting buy again
				if (curr[symbol][0] is None and curr[symbol][1] == 0) or (not curr[symbol][0].is_alive()):
					curr[symbol][0] = None
					curr[symbol][1] = amount
					succeeded = True
			except Exception:
				curr[symbol] = [None, amount, 0]
				succeeded = True
		except KeyError:
			self.timers[ver][user] = {symbol: [None, amount, 0]}
			succeeded = True
		return succeeded

	# TransactionServer must add the amount returned to account balance
	def cancel(self, ver, user, symbol):
		amount = -1
		try:
			curr = self.timers[ver][user]
			try:
				if not curr[symbol][0] is None:
					if curr[symbol][0].is_alive():
						# Kill QuoteThread if running
						curr[symbol][0].join()
						curr[symbol][0] = None
					else:
						curr[symbol][0] = None
						curr[symbol][1] = 0			
					amount = curr[symbol][1]	
				elif curr[symbol][1] > 0:			
					amount = curr[symbol][1]
				curr[symbol][1] = 0
			except KeyError:
				curr[symbol] = [None, 0, 0]
		except KeyError:
			self.timers[ver][user] = {symbol: [None, 0, 0]}
		return amount

	def trigger(self, ver, user, symbol, price):
		succeeded = False
		try:
			curr = self.timers[ver][user]
			try:
				# Can only trigger if amount > 0, and present thread DNE or is dead
				if (curr[symbol][0] is None or not curr[symbol][0].is_alive()) and curr[symbol][1] > 0:
					curr[symbol][2] = price
					curr[symbol][0] = QuoteThread(self.cli_data, self.cache, ver, user, symbol, curr[symbol][1], price)
					curr[symbol][0].start()
					succeeded = True
			except Exception:
				curr[symbol] = [None, 0, 0]
		except KeyError:
			self.timers[ver][user] = {symbol: [None, 0, 0]}
		return succeeded
		
	def state(self, user):
		curr = {"buy":{}, "sel":{}}
		try:
			curr["buy"] = self.timers["buy"][user]
			curr["sel"] = self.timers["sel"][user]
		except KeyError:
			pass
		return curr
