import socket
import threading
import time


class QuoteCache:
    def __init__(self, addr, port):

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((addr, port))
        except Exception as e:
            print("quote_server:", end="")
            print(e)

        # Simulating DB with dictionary
        self.quotes = dict()
        self.lock = threading.Lock()

    def new_quote(self, symbol, user):
        self.conn.sendall(str.encode(symbol + ", " + user + "\n"))
        print("->quote_server 'quote request' sent\n->waiting for response...")
        data = self.conn.recv(1024).decode().split(",")

        # STUB
        #data = ["20.87", symbol, user, time.time(), "QWERTYUIOP"]

        # print(data)
        data[0] = float(data[0])
        qtm = time.time()
        self.quotes[symbol] = (qtm, data)

        return data

    def quote(self, symbol, user):
        val = []
        self.lock.acquire()
        try:
            q = self.quotes.get(symbol)  # get previous quote if exists
            if q is None or time.time() - q[0] >= 60:
                val = self.new_quote(symbol, user)
            else:
                val = q[1]
        except KeyError:
            val = self.new_quote(symbol, user)
        print(str(val))
        self.lock.release()
        return val
