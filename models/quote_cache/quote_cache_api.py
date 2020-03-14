from flask import Flask, app, request
from quote_cache import quote_cache
import json.tool
import os
app = Flask(__name__)

redis_host = os.environ.get("REDIS_HOST", default="localhost")
redis_port = os.environ.get("REDIS_PORT", default=6379)
quote_cache_ip = os.environ.get('MY_HOST', default="localhost")
quote_cache_port = os.environ.get('MY_PORT', default=44418)

quote_cache_instance = None

@app.route("/cache_quote", methods=["POST"])
def cache_quote():
    data = request.json
    response = quote_cache_instance.cache_quote(data)
    return json.dumps(response)

@app.route("/get_quote/<string:stock_symbol>", methods=["GET"])
def get_quote(stock_symbol):
    response = quote_cache_instance.get_quote(stock_symbol)
    return json.dumps(response)

if __name__ == "__main__":
    quote_cache_instance = quote_cache(redis_host=redis_host, redis_port=redis_port)
    app.run(host=quote_cache_ip, port=quote_cache_port)