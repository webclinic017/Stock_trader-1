import redis
import threading
class quote_cache:
    def __init__(self, redis_host, redis_port):
        self.r = redis.Redis(host=redis_host, port=redis_port)
        self.mutex = threading.Lock()

    def sanitize_byte_keys_and_vals(self, response):
        sanitized_dict = {}
        keys = response.keys()
        for key in keys:
            sanitized_dict[str(key, encoding="utf-8")] = str(response[key], encoding="utf-8")
        return sanitized_dict

    def cache_quote(self, data):
        print("quote_cache.cache_quote TRACE1")
        stock_symbol = data["stock_symbol"]
        dollars = data["dollars"]
        cents = data["cents"]
        quote_time = data["quote_time"]
        cryptokey = data["cryptokey"]
        response = {}
        print("quote_cache.cache_quote TRACE2")

        self.mutex.acquire()
        print("quote_cache.cache_quote MUTEX ACQUIRED")

        try:
            bool_result = self.r.hmset(stock_symbol, {"dollars": dollars, "cents": cents, "quote_time": quote_time, "cryptokey": cryptokey})
            print("quote_cache.cache_quote TRACE3")
            if (bool_result):
                response["status"] = "SUCCESS"
            else:
                response["status"] = "ERROR"
            print("quote_cache.cache_quote TRACE4")

        finally:
            self.mutex.release()
            print("quote_cache.cache_quote MUTEX RELEASED")

        return response

    def get_quote(self, stock_symbol):
        response = {"status": "ERROR"}
        response["data"] = self.sanitize_byte_keys_and_vals(self.r.hgetall(stock_symbol))
        if (response["data"] != None and len(response["data"]) != 0):
            response["status"] = "SUCCESS"
        return response