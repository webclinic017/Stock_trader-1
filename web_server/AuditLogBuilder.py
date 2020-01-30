import uuid
import time
class AuditLogBuilder:
    _audit_log = {}
    def __init__(self, command, server):
        self._server = server
        try:
            self.build = self._func_wrapper(build_func=self._method[command])
        except KeyError:
            pass

    def build(self):
        pass

    def _add(self):
        audit_log = self._audit_log
        audti_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "funds": data["amount"]
        }
        return audit_log

    def _quote(self):
        audit_log = self._audit_log
        audit_log["data_fields"] = {
            "price": data["Quote"],
            "stockSymbol": data["StockSymbol"],
            "username": data["userid"],
            "quoteServerTime": data["quoteServerTime"],
            "cryptokey": data["cryptokey"]
        }
        return audit_log

    def _buy(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return audit_log

    def _commit_buy(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "amount": data["amount"]
        }
        return audit_log

    def _cancel_buy(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return audit_log

    def _sell(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return audit_log

    def _commit_sell(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return audit_log

    def _cancel_sell(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return audit_log

    def _set_buy_amount(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return audit_log

    def _cancel_set_buy(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return audit_log

    def _set_buy_trigger(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return audit_log

    def _set_sell_amount(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return audit_log

    def _set_sell_trigger(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return audit_log

    def _cancel_set_sell(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return audit_log

    def _dumplog(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "filename": data["filename"]
        }
        return audit_log

    def _display_summary(self):
        audit_log = self._audit_log
        audit_log["commandType"] = "userCommand"
        audit_log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return audit_log

    def _func_wrapper(build_func):
        def func(self, data):
            self._audit_log = {
                "transactionId": str(uuid.uuid4()),
                "data_fields": {
                    "timestamp": int(time.time()),
                    "server": self._server
                }
            }
            return build_func()
        return func

    _method = {
        "ADD": _add,
        "QUOTE": _quote,
        "BUY": _buy,
        "COMMIT_BUY": _commit_buy,
        "CANCEL_BUY": _cancel_buy,
        "SELL": _sell,
        "COMMIT_SELL": _commit_sell,
        "CANCEL_SELL": _cancel_sell,
        "SET_BUY_AMOUNT": _set_buy_amount,
        "CANCEL_SET_BUY": _cancel_set_buy,
        "SET_BUY_TRIGGER": _set_buy_trigger,
        "SET_SELL_AMOUNT": _set_sell_amount,
        "SET_SELL_TRIGGER": _set_sell_trigger,
        "CANCEL_SET_SELL": _cancel_set_sell,
        "DUMPLOG": _dumplog,
        "DISPLAY_SUMMARY": _display_summary
    }