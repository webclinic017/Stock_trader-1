from flask import Flask, app, request
from user import user
import json.tool
app = Flask(__name__)

redis_host = "127.0.0.1"
redis_port = 6379
user_persist_ip = "localhost"
user_persist_port = 44417

user_instance = None

@app.route("/current_funds/<string:username>", methods=["GET"])
def current_funds(username):
    response = user_instance.user_funds(username)
    return json.dumps(response) # {username: string, dollars: int, cents: int}

@app.route("/current_stock/<string:username/<string:stock_symbol>", methods=["GET"])
def current_stock(username, stock_symbol):
    response = user_instance.number_of_stocks(username, stock_symbol)
    return json.dumps(response)

@app.route("/commit_buy", methods=["POST"])
def commit_buy():
    data = request.json
    username = data["username"]
    stock_symbol = data["stock_symbol"]
    stock_price_dollars = data["stock_price_dollars"]
    stock_price_cents = data["stock_price_cents"]
    dollars_delta = -1 * data["dollars_delta"]
    cents_delta = -1 * data["cents_delta"]
    response = user_instance.stock_delta(data)
    return json.dumps(response)

@app.route("/commit_sell", methods=["POST"])
def commit_sell():
    data = request.json
    username = data["username"]
    stock_symbol = data["stock_symbol"]
    stock_price_dollars = data["stock_price_dollars"]
    stock_price_cents = data["stock_price_cents"]
    dollars_delta = data["dollars_delta"]
    cents_delta = data["cents_delta"]
    response = user_instance.stock_delta(username, stock_symbol, stock_price_dollars, stock_price_cents, dollars_delta, cents_delta)
    return json.dumps(response)

@app.route("/add_funds", methods=["POST"])
def add_funds():
    data = request.json
    username = data["username"]
    dollars = data["dollars"]
    cents = data["cents"]
    response = user_instance.add_funds_delta(username, dollars, cents)
    return response

@app.route("/create_new_user", methods="POST")
def create_new_user():
    data = request.json
    username = data["username"]
    response = user_instance.create_new_user(username)
    return json.dumps(response)

@app.route("/set_buy_trigger", methods=["POST"])
def set_buy_trigger():
    data = request.json
    username = data["username"]
    stock_symbol = data["stock_symbol"]
    dollars = data["dollars"]
    cents = data["cents"]
    response = user.set_buy_trigger(user.TriggerTypes.BUY, username, stock_symbol, dollars, cents)
    return json.dumps(response)

@app.route("/set_sell_trigger", methods=["POST"])
def set_buy_trigger():
    data = request.json
    username = data["username"]
    stock_symbol = data["stock_symbol"]
    dollars = data["dollars"]
    cents = data["cents"]
    response = user.set_buy_trigger(user.TriggerTypes.SELL, username, stock_symbol, dollars, cents)
    return json.dumps(response)

if __name__ == "__main__":
    user_instance = user(redis_host=redis_host, redis_port=redis_port)
    app.run(host=user_persist_ip, port=user_persist_port)