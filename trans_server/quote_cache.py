import socket
import time
from audit_logger.AuditLogBuilder import AuditLogBuilder
from audit_logger.AuditCommandType import AuditCommandType
BUFFER_SIZE = 4096
import requests
from currency import Currency

class QuoteCacheUrls:
    CACHE_QUOTE = "cache_quote"
    GET_QUOTE = "get_quote"

class QuoteCache:
    def __init__(self, server_name, protocol):
        self.load_env()
        self._server_name = server_name
        self.quote_cache_server_url = f"{protocol}://{self.quote_cache_host}:{self.quote_cache_port}"

    def load_env(self):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.quote_cache_host = os.environ.get("quote_cache_host")
        self.quote_cache_port = os.environ.get("quote_cache_port")
        self.quote_server_host = os.environ.get("quote_server_host")
        self.quote_server_port = os.environ.get("quote_server_port")
        self.quote_server = os.environ.get("quote_server")

    def new_quote(self, symbol, user):
        if (self.quote_server):
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.conn.connect((self.quote_server_host, self.quote_server_port))
                self.conn.sendall(str.encode(symbol + ", " + user + "\n"))
                print("->quote_server 'quote request' sent\n->waiting for response...")
                data = self.conn.recv(BUFFER_SIZE).decode().split(",")
                self.conn.close()
            except Exception as e:
                print(e)
        else:
            time.sleep(2)
            data = ["20.87", symbol, user, time.time(), "QWERTYUIOP"]

        qtm = time.time()
        amount = Currency(data[0])
        data[0] = amount
        cryptokey = data[4]
        requests.post(
            f"{self.quote_cache_server_url}/{QuoteCacheUrls.CACHE_QUOTE}",
            json={
                "stock_symbol": symbol,
                "dollars": amount.dollars,
                "cents": amount.cents,
                "quote_time": qtm,
                "cryptokey": cryptokey
            }
        )

        AuditLogBuilder("QUOTE", self._server_name, AuditCommandType.quoteServer).build({
            "Quote": data[0],
            "StockSymbol": data[1],
            "userid": data[2],
            "quoteServerTime": data[3],
            "cryptokey": data[4]
        }).send()

        return data

    def quote(self, symbol, user):
        val = []
        try:
            response = requests.get(f"{self.quote_cache_server_url}/{QuoteCacheUrls.GET_QUOTE}/{symbol}").json()
            if (response["status"] != "SUCCESS" or (time.time() - float(response["data"]["quote_time"])) >= 60):
                val = self.new_quote(symbol, user)
            else:
                data = response["data"]
                quote_time = data["quote_time"]
                quote_amount = Currency(data["dollars"]) + Currency(data["cents"])
                cryptokey = data["cryptokey"]
                val = [quote_amount, symbol, user, quote_time, cryptokey]
        except KeyError as e:
            val = self.new_quote(symbol, user)
        return val
