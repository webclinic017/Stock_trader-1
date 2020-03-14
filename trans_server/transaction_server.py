import select
import socket
import json
from event_server import QuoteThread
from audit_logger.AuditLogBuilder import AuditLogBuilder
from audit_logger.AuditCommandType import AuditCommandType
from currency import Currency

BUFFER_SIZE = 4096

# noinspection PyRedundantParentheses
class TransactionServer:
    # Create a server socket then bind and listen the socket
    def __init__(self, cli_data, cache, events, addr, port, server_name):
        self._server_name = server_name
        self.cli_data = cli_data
        self.cache = cache
        self.events = events
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((addr, int(port)))
        self.server.listen(10)

    ##### Base Commands #####
    def add(self, data):
        user = data["userid"]
        AuditLogBuilder("ADD", self._server_name, AuditCommandType.userCommand).build(data).send()
        amount = data["amount"]
        return self.cli_data.add_money(user, amount)

    def quote(self, data):
        AuditLogBuilder("QUOTE", self._server_name, AuditCommandType.userCommand).build(data).send()
        quote_data = self.cache.quote(data["StockSymbol"], data["userid"])
        data["Quote"] = quote_data[0]
        data["quoteServerTime"] = quote_data[3]
        data["cryptokey"] = quote_data[4]
        return True

    ###### Buy Commands #####
    def buy(self, data):
        AuditLogBuilder("BUY", self._server_name, AuditCommandType.userCommand).build(data).send()

        succeeded = False
        user = data["userid"]

        amount = Currency(data["amount"])
        user_funds = self.cli_data.check_money(user)

        if ((user_funds - amount) > 0):

            self.cli_data.push(user, data["StockSymbol"], float(amount), "buy")

            succeeded = True
        return succeeded

    def commit_buy(self, data):
        AuditLogBuilder("COMMIT_BUY", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        buy_data = self.cli_data.pop(user, "buy")
        if (len(buy_data) == 0):
            raise Exception("pop() performed on empty buy stack")
        else:
            print("popped from NONEMPTY buy stack")
        stock_symbol = buy_data["stock_symbol"]
        price = Currency(self.cache.quote(stock_symbol, user)[0])
        buy_amount = Currency(buy_data["dollars"]) + Currency(buy_data["cents"])

        # Return the delta of the transaction to user's account
        self.cli_data.commit_buy(user, stock_symbol, price, buy_amount)
        succeeded = True
        return succeeded

    def cancel_buy(self, data):
        AuditLogBuilder("CANCEL_BUY", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        try:
            self.cli_data.pop(user, "buy")
            succeeded = True
        except Exception:
            pass
        return succeeded

    ###### Sell Commands #####
    def sell(self, data):
        AuditLogBuilder("SELL", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        dollar_amt_to_sell = float(data["amount"])
        symbol = data["StockSymbol"]
        price = self.cache.quote(symbol, user)[0]
        stocks_on_hand = int(self.cli_data.get_stock_held(user, symbol))
        if stocks_on_hand > 0:
            self.cli_data.push(user, data["StockSymbol"], dollar_amt_to_sell, "sell")
            succeeded = True
        return succeeded

    def commit_sell(self, data):
        AuditLogBuilder("COMMIT_SELL", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        cli_data = self.cli_data

        sell_data = cli_data.pop(user, "sell")
        if (len(sell_data) == 0):
            raise Exception("pop() performed on empty sell stack")
        symbol = sell_data["stock_symbol"]

        shares_on_hand = cli_data.get_stock_held(user, symbol)

        price = self.cache.quote(symbol, user)[0]
        shares_to_sell = int(int(sell_data["dollars"]) / price)
        if shares_to_sell <= shares_on_hand:
            cli_data.commit_sell(user, symbol, price, shares_to_sell)
        succeeded = True

        self.cli_data = cli_data
        return succeeded

    def cancel_sell(self, data):
        AuditLogBuilder("CANCEL_SELL", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        try:
            self.cli_data.pop(user, "sell")
            succeeded = True
        except Exception:
            pass
        return succeeded

    ###### Buy Trigger Commands #####
    def set_buy_amount(self, data):
        AuditLogBuilder("SET_BUY_AMOUNT", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        symbol = data["StockSymbol"]
        amount = float(data["amount"])

        if self.events.register("buy", user, symbol, amount):
            succeeded = True
        return succeeded

    def cancel_set_buy(self, data):
        AuditLogBuilder("CANCEL_SET_BUY", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        symbol = data["StockSymbol"]

        self.events.cancel("buy", user, symbol)
        return succeeded

    def set_buy_trigger(self, data):
        AuditLogBuilder("SET_BUY_TRIGGER", self._server_name, AuditCommandType.userCommand).build(data).send()
        user = data["userid"]
        symbol = data["StockSymbol"]
        price = float(data["amount"])

        result = self.events.trigger("buy", user, symbol, price)
        return result

    ###### Sell Trigger Commands #####
    def set_sell_amount(self, data):
        AuditLogBuilder("SET_SELL_AMOUNT", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        symbol = data["StockSymbol"]
        amount = int(float(data["amount"]))

        if self.events.register("sel", user, symbol, amount):
            succeeded = True
        return succeeded

    def cancel_set_sell(self, data):
        AuditLogBuilder("CANCEL_SET_SELL", self._server_name, AuditCommandType.userCommand).build(data).send()
        succeeded = False
        user = data["userid"]
        symbol = data["StockSymbol"]

        self.events.cancel("sel", user, symbol)
        return succeeded

    def set_sell_trigger(self, data):
        AuditLogBuilder("SET_SELL_TRIGGER", self._server_name, AuditCommandType.userCommand).build(data).send()
        user = data["userid"]
        symbol = data["StockSymbol"]
        price = float(data["amount"])  # Sell shares at this price or higher

        result = self.events.trigger("sel", user, symbol, price)
        return result

    ##### Audit Commands #####
    def display_summary(self, data):

        user = data["userid"]

        acc = self.cli_data.get_user(user)

        tri = self.events.state(user)

        buy_triggers_keys = tri["buy"].keys()
        sell_triggers_keys = tri["sel"].keys()
        tri_copy = {"buy": {}, "sel": {}}

        for stock_sym in buy_triggers_keys:
            tri_copy["buy"][stock_sym] = str(tri["buy"][stock_sym])
        for stock_sym in sell_triggers_keys:
            tri_copy["sel"][stock_sym] = str(tri["sel"][stock_sym])

        log_data = acc.copy()
        log_data["userid"] = data["userid"]
        log_data["Command"] = "DISPLAY_SUMMARY"
        AuditLogBuilder("DISPLAY_SUMMARY", self._server_name, AuditCommandType.userCommand).build(log_data).send()

        return {"Account": acc, "Triggers": tri_copy}

    # Command entry point
    def transaction(self, conn):
        # TODO: We should consider creating a queue for the incoming commands.
        incoming_data = conn.recv(BUFFER_SIZE).decode()
        if incoming_data == "":
            return False

        # DEBUG

        try:
            try:
                data_payload_list = [json.loads(incoming_data)]
            except ValueError as v:
                data_payload_list = []
                split_data = incoming_data.split("}{")
                for partial_json_str in split_data:
                    json_str = partial_json_str
                    if (partial_json_str[0] != "{"):
                        json_str = "{" + json_str
                    if (partial_json_str[len(partial_json_str) - 1] != "}"):
                        json_str = json_str + "}"
                    json_data = json.loads(json_str)
                    data_payload_list.append(json_data)

            for data in data_payload_list:
                print(data)
                if (type(data) == str):
                    data = json.loads(data)
                command = data["Command"]

                if command == "ADD":
                    data["Succeeded"] = self.add(data)
                elif command == "QUOTE":
                    data["Succeeded"] = self.quote(data)
                elif command == "BUY":
                    data["Succeeded"] = self.buy(data)
                elif command == "COMMIT_BUY":
                    data["Succeeded"] = self.commit_buy(data)
                elif command == "CANCEL_BUY":
                    data["Succeeded"] = self.cancel_buy(data)
                elif command == "SELL":
                    data["Succeeded"] = self.sell(data)
                elif command == "COMMIT_SELL":
                    data["Succeeded"] = self.commit_sell(data)
                elif command == "CANCEL_SELL":
                    data["Succeeded"] = self.cancel_sell(data)
                elif command == "SET_BUY_AMOUNT":
                    data["Succeeded"] = self.set_buy_amount(data)
                elif command == "CANCEL_SET_BUY":
                    data["Succeeded"] = self.cancel_set_buy(data)
                elif command == "SET_BUY_TRIGGER":
                    data["Succeeded"] = self.set_buy_trigger(data)
                elif command == "SET_SELL_AMOUNT":
                    data["Succeeded"] = self.set_sell_amount(data)
                elif command == "CANCEL_SET_SELL":
                    data["Succeeded"] = self.cancel_set_sell(data)
                elif command == "SET_SELL_TRIGGER":
                    data["Succeeded"] = self.set_sell_trigger(data)
                elif command == "DISPLAY_SUMMARY":
                    data["Data"] = self.display_summary(data)
                    # TR-The lower section was overwriting the actual triggers
                    # buy_triggers_keys = data["Data"]["Triggers"]["buy"].keys()
                    # sell_triggers_keys = data["Data"]["Triggers"]["sel"].keys()
                    # for stock_sym in buy_triggers_keys:
                    #     data["Data"]["Triggers"]["buy"][stock_sym][0] = str(data["Data"]["Triggers"]["buy"][stock_sym][0])
                    # for stock_sym in sell_triggers_keys:
                    #     data["Data"]["Triggers"]["sel"][stock_sym][0] = str(data["Data"]["Triggers"]["sel"][stock_sym][0])
                # Echo back JSON with new attributes
                conn.send(str.encode(json.dumps(data, cls=Currency)))

        except Exception as e:
            print(e)
            AuditLogBuilder("ERROR", self._server_name, AuditCommandType.errorEvent).build({"errorMessage": str(e)}).send()
            conn.send(str.encode("{\"FAILED\"}"))
            return False
        return True

    # Non-return function launches the server loop
    def launch(self):
        open_sockets = []
        try:
            while True:
                rlist, wlist, xlisst = select.select([self.server] + open_sockets, [], [])
                for s in rlist:
                    if s is self.server:
                        conn, addr = self.server.accept()
                        open_sockets.append(conn)
                    else:
                        try:
                            if not self.transaction(s):
                                try:
                                    s.shutdown(socket.SHUT_RDWR)
                                    s.close()
                                except OSError:
                                    pass
                                open_sockets.remove(s)
                        except ConnectionResetError:
                            print("connection reset by peer")
                            pass
        except KeyboardInterrupt:
            for s in open_sockets:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
