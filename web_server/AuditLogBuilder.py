import uuid
import time
import requests
import json
class AuditLogBuilder:
    def __init__(self, command, server):
        self._audit_log = {}
        self._server = server
        try:
            self.build = self._func_wrapper(self._method[command])
        except KeyError:
            pass

    def build(self, data):
        return self

    def _add(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "funds": data["amount"]
        }
        return log

    def _quote(self, data):
        log = {}
        log["commandType"] = "QuoteServerType"
        log["data_fields"] = {
            "price": data["Quote"],
            "stockSymbol": data["StockSymbol"],
            "username": data["userid"],
            "quoteServerTime": data["quoteServerTime"],
            "cryptokey": data["cryptokey"]
        }
        return log

    def _buy(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return log

    def _commit_buy(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "amount": data["amount"]
        }
        return log

    def _cancel_buy(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return log

    def _sell(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return log

    def _commit_sell(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return log

    def _cancel_sell(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return log

    def _set_buy_amount(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return log

    def _cancel_set_buy(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return log

    def _set_buy_trigger(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return log

    def _set_sell_amount(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return log

    def _set_sell_trigger(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": data["amount"]
        }
        return log

    def _cancel_set_sell(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return log

    def _dumplog(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "filename": data["filename"]
        }
        return log

    def _display_summary(self, data):
        log = {}
        log["commandType"] = "UserCommandType"
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return log

    def _func_wrapper(self, build_func):
        def func(data_json_str):
            data = json.loads(data_json_str)
            transactionId = str(uuid.uuid4())
            audit_log = self._audit_log
            audit_log[transactionId] = build_func(self, data)
            audit_log[transactionId]["data_fields"]["timestamp"] = int(time.time())
            audit_log[transactionId]["data_fields"]["server"] = self._server
            self._audit_log = audit_log
            return self
        return func

    def send(self, protocol, audit_log_server_ip, audit_log_server_port):
        requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", json=self._audit_log)

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