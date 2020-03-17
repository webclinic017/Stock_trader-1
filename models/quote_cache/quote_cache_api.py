from flask import Flask, app, request
from quote_cache import quote_cache
import json.tool
import os

app = Flask(__name__)

quote_cache_instance = quote_cache()

@app.route("/cache_quote", methods=["POST"])
def cache_quote():
    data = request.json
    response = quote_cache_instance.cache_quote(data)
    return json.dumps(response)

@app.route("/get_quote/<string:stock_symbol>", methods=["GET"])
def get_quote(stock_symbol):
    response = quote_cache_instance.get_quote(stock_symbol)
    return json.dumps(response)