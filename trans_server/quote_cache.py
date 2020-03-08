import socket
import threading
import time
from audit_logger.AuditLogBuilder import AuditLogBuilder
from audit_logger.AuditCommandType import AuditCommandType
BUFFER_SIZE = 4096
LOG_ENABLED = False
PRINT_ENABLED = False

class QuoteCache:
    def __init__(self, addr, port, should_stub, server_name):
        self._server_name = server_name
        self._addr = addr
        self._port = port
        self._should_stub = should_stub

        # Simulating DB with dictionary
        self.quotes = dict()
        self.lock = threading.Lock()

    def new_quote(self, symbol, user):
        addr = self._addr
        port = self._port
        if (not self._should_stub):
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.conn.connect((addr, port))
                self.conn.sendall(str.encode(symbol + ", " + user + "\n"))
                if PRINT_ENABLED:print("->quote_server 'quote request' sent\n->waiting for response...")
                data = self.conn.recv(BUFFER_SIZE).decode().split(",")
                self.conn.close()
            except Exception as e:
                print(e)
        else:
            time.sleep(2)  # testing
            data = ["20.87", symbol, user, time.time(), "QWERTYUIOP"]

        # print(data)
        data[0] = float(data[0])
        qtm = time.time()

        # TR-Update the quote cache
        self.lock.acquire()
        self.quotes[symbol] = (qtm, data)
        self.lock.release()

        if LOG_ENABLED: AuditLogBuilder("QUOTE", self._server_name, AuditCommandType.quoteServer).build({
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
            self.lock.acquire()
            q = self.quotes.get(symbol)  # get previous quote if exists
            self.lock.release()
            if q is None or time.time() - q[0] >= 60:
                val = self.new_quote(symbol, user)
            else:
                val = q[1]
        except KeyError:
            val = self.new_quote(symbol, user)
        if PRINT_ENABLED:print(str(val))
        return val
