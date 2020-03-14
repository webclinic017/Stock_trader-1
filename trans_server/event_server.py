import threading
from audit_logger.AuditLogBuilder import AuditLogBuilder
from audit_logger.AuditCommandType import AuditCommandType
from currency import Currency

class QuoteThread(threading.Thread):
	def __init__(self, cli_data, cache, ver, user, symbol, amount, price):
		super().__init__()
		self.ver = ver
		self.cli_data = cli_data
		self.cache = cache
		self.user = user
		self.symbol = symbol
		self.amount = Currency(amount)
		self.price = Currency(price)
		self.stopevent = threading.Event()

	def run(self):
		while not self.stopevent.isSet():
			quote = Currency(self.cache.quote(self.symbol, self.user)[0])

			if self.ver == "buy" and quote <= self.price:
				self.cli_data.commit_buy(username=self.user, stock_symbol=self.symbol, price=quote, buy_amount=self.amount)
				break
			elif self.ver == "sel" and quote >= self.price:
				count = int(self.price.dollars / quote.dollars)
				self.cli_data.commit_sell(username=self.user, stock_symbol=self.symbol, price=quote, count=count)
				break
			self.stopevent.wait(60.0)

	def join(self):
		self.stopevent.set()
		threading.Thread.join(self, None)

	def __str__(self):
		return "active"

	def __repr__(self):
		return "active"

	def __dict__(self):
		return {"objectType": "QuoteThread", "status": "active"}


class EventServer:
	def __init__(self):
		self.timers = {"buy": {}, "sel": {}}

	def give_hooks(self, cli_data, cache):
		self.cache = cache
		self.cli_data = cli_data

	def register(self, ver, user, symbol, amount):
		succeeded = False
		try:
			curr = self.timers[ver][user]
			try:
				event = curr[symbol]
				# Buy trigger already running, must cancel before setting buy again
				if (event[0] is None and event[1] == 0) or (not event[0].is_alive()):
					event[0] = None
					event[1] = amount
					succeeded = True
			except Exception:
				curr[symbol] = [None, amount, 0]
				succeeded = True
		except KeyError:
			self.timers[ver][user] = {symbol: [None, amount, 0]}
			succeeded = True
		return succeeded

	def cancel(self, ver, user, symbol):
		amount = -1
		try:
			curr = self.timers[ver][user]
			try:
				event = curr[symbol]
				try:
					if event[0] is not None:
						if event[0].is_alive():
							# Kill QuoteThread if running
							event[0].join()
						else:
							event[1] = 0
						event[0] = None
						amount = event[1]
					elif event[1] > 0:
						amount = event[1]
					event[1] = 0
					self.timers[ver][user].pop(symbol)
				except Exception as e:
					AuditLogBuilder("ERROR", "event_server", AuditCommandType.errorEvent).build({
						"Command": "CANCEL_SET_BUY",
						"errorMessage": str(e)
					}).send()
			except KeyError:
				pass  # TR-added
				# curr[symbol] = [None, 0, 0]  # TR-This line makes no sense, why add an empty trigger?
		except KeyError:
			pass  # TR-added
			# self.timers[ver][user] = {symbol: [None, 0, 0]}  # TR-This line also makes no sense to execute
		return amount

	def trigger(self, ver, user, symbol, price):
		succeeded = False
		try:
			curr = self.timers[ver][user]
			try:
				event = curr[symbol]
				# Can only trigger if amount > 0, and present thread DNE or is dead
				if (event[0] is None or not event[0].is_alive()) and event[1] > 0:
					event[2] = price
					event[0] = QuoteThread(self.cli_data, self.cache, ver, user, symbol, event[1], price)
					event[0].start()
					succeeded = True
			except Exception:
				pass  # TR-added
				# curr[symbol] = [None, 0, 0]  # TR-This line makes no sense, why add an empty trigger?
		except KeyError:
			pass  # TR-added
			# self.timers[ver][user] = {symbol: [None, 0, 0]}  # TR-This line also makes no sense to execute
		return succeeded

	def state(self, user):
		curr = {"buy": {}, "sel": {}}
		try:
			curr["buy"] = self.timers["buy"][user]
			curr["sel"] = self.timers["sel"][user]
		except KeyError:
			pass
		return curr
