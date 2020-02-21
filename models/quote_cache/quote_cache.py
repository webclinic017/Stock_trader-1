import redis

class quote_cache():

    def __init__(self, redis_host, redis_port):
        self.r = redis.Redis(host=redis_host, port=redis_port)

    def cache_quote(self, stock_symbol, dollars, cents):
        response = {}
        response["data"] = self.r.hset(stock_symbol, "dollars", dollars, "cents", cents)
        response["status"] = "SUCCESS"
        return response

    def get_quote(self, stock_symbol):
        response = {"status": "ERROR"}
        response["data"] = self.r.hgetall(stock_symbol)
        if (response["data"] != None and len(response["data"]) != 0):
            response["status"] = "SUCCESS"
        return response