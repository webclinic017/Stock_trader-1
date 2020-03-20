import uuid
import time
import requests
import json
from audit_logger.AuditCommandType import AuditCommandType
import os
from dotenv import load_dotenv
load_dotenv()
audit_log_server_ip = os.environ.get('audit_log_host')
audit_log_server_port = os.environ.get('audit_log_port')
class AuditLogBuilder:
    def __init__(self, command, server, commandType):
        self._audit_log_server_ip = audit_log_server_ip
        self._audit_log_server_port = audit_log_server_port
        self._protocol = "http"
        self._audit_log = {}
        self._server = server
        self._commandType = commandType
        try:
            self.build = self._func_wrapper(self._method[command])
        except KeyError:
            pass

    def build(self, data):
        return self

    def _accountUpdate(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "username": data["userid"],
            "funds": str(data["amount"])
        }
        if self._commandType == AuditCommandType.userCommand:
            log["data_fields"]["command"] = data["Command"]
        else:
            log["data_fields"]["action"] = data["action"]
        return log

    def _quote(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "stockSymbol": data["StockSymbol"],
            "username": data["userid"],
        }
        if (self._commandType == AuditCommandType.userCommand):
            log["data_fields"]["command"] = data["Command"]
        else:
            log["data_fields"]["price"] = str(data["Quote"])
            log["data_fields"]["quoteServerTime"] = int(data["quoteServerTime"])
            log["data_fields"]["cryptokey"] = data["cryptokey"]
        return log

    def _buy(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": str(data["amount"])
        }
        return log

    def _commit_buy(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return log

    def _cancel_buy(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return log

    def _sell(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": str(data["amount"])
        }
        return log

    def _commit_sell(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return log

    def _cancel_sell(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return log

    def _set_buy_amount(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": str(data["amount"])
        }
        return log

    def _cancel_set_buy(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return log

    def _set_buy_trigger(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": str(data["amount"])
        }
        return log

    def _set_sell_amount(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": str(data["amount"])
        }
        return log

    def _set_sell_trigger(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"],
            "funds": str(data["amount"])
        }
        return log

    def _cancel_set_sell(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "stockSymbol": data["StockSymbol"]
        }
        return log

    def _dumplog(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"],
            "filename": data["filename"]
        }
        return log

    def _display_summary(self, data):
        # print("DISPLAY_SUMMARY DATA:")
        # print(data)
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "command": data["Command"],
            "username": data["userid"]
        }
        return log

    def _error(self, data):
        log = {}
        log["commandType"] = self._commandType
        log["data_fields"] = {
            "errorMessage": data["errorMessage"]
        }
        return log

    def _get_appropriate_transaction_num(self):
        if (self._commandType == "userCommand"):
            return self._get_next_transaction_num()
        else:
            return self._get_current_transaction_num()

    def _get_current_transaction_num(self):
        return requests.post(
            f"{self._protocol}://{self._audit_log_server_ip}:{self._audit_log_server_port}/getCurrentTransactionNum")

    def _get_next_transaction_num(self):
        return requests.post(
            f"{self._protocol}://{self._audit_log_server_ip}:{self._audit_log_server_port}/getNextTransactionNum")

    def send(self):
        requests.post(f"{self._protocol}://{self._audit_log_server_ip}:{self._audit_log_server_port}/auditLog",
                      json=self._audit_log)

    def _func_wrapper(self, build_func):
        def func(data):
            transactionId = str(uuid.uuid4())
            audit_log = self._audit_log
            transaction_num_response = self._get_appropriate_transaction_num().json()
            if transaction_num_response["status"] == "SUCCESS":
                transaction_num = transaction_num_response["data"]
                audit_log[transactionId] = build_func(self, data)
                audit_log[transactionId]["data_fields"]["transactionNum"] = transaction_num
                audit_log[transactionId]["data_fields"]["timestamp"] = int(time.time()) * 1000
                audit_log[transactionId]["data_fields"]["server"] = self._server
            else:
                raise Exception(
                    f"\033[1;31mError: could not communicate with the audit log server to obtain the transaction number of the current {self._commandType}\033[0;0m")
            self._audit_log = audit_log
            return self

        return func

    _method = {
        "ADD": _accountUpdate,
        "REMOVE": _accountUpdate,
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
        "DISPLAY_SUMMARY": _display_summary,
        "ERROR": _error
    }
