import redis
import json
class user_accounts():
    class TriggerTypes():
        BUY = "buy_triggers"
        SELL = "sell_triggers"
    def __init__(self, redis_host, redis_port):
        self.r = redis.Redis(host=redis_host, port=redis_port)

    def create_new_user(self, username):
        self.r.hset(username, "stocks", "{}", "dollars", 0, "cents", 0, "buy_triggers", "{}", "sell_triggers", "{}")

    def user_funds(self, username):
        user = self.r.hgetall(username)
        dollars = user["dollars"]
        cents = user["cents"]
        return {"username": username, "dollars": dollars, "cents": cents}

    def number_of_stocks(self, username, stock_symbol):
        try:
            num_stocks =  self.r.hget(username, "stocks")[stock_symbol]
        except KeyError:
            num_stocks = 0
        return num_stocks

    def stock_delta(self, 
                    username, 
                    stock_symbol, 
                    stock_price_dollars, 
                    stock_price_cents, 
                    dollars_delta, 
                    cents_delta):
        try:
            updated_funds = self.add_funds_delta(username, dollars_delta, cents_delta)
            #if (updated_funds["status"] != "SUCCESS"):
            #    response = updated_funds
            #    return response
            amount_delta = dollars_delta + (cents_delta / 100)
            stock_price = (stock_price_dollars + (stock_price_cents / 100))
            stock_delta_value = int(amount_delta / stock_price)
            stocks = json.loads(self.r.hget(username, "stocks"))
            stocks[stock_symbol] = stocks[stock_symbol] + stock_delta_value
        except KeyError:
            #if (stock_delta_value < 0): # sell condition
            #    return {"username": username, f"status": "ERROR: insufficient number of {stock_symbol} stock to sell"}
            stocks[stock_symbol] = stock_delta_value
        stocks_str = json.dumps(stocks)
        self.r.hset(username, "dollars", updated_funds["dollars"], "cents", updated_funds["cents"], "stocks", stocks_str)
        response = updated_funds
        response["stocks"] = stocks_str
        return response

    def add_funds_delta(self, username, dollars_delta, cents_delta):
        funds_delta = dollars_delta + (cents_delta / 100)
        user = r.hgetall(username)
        cents = user["cents"]
        dollars = user["dollars"]
        #if (funds_delta < 0 and (abs(funds_delta) > (dollars + (cents / 100)))):
        #    return {"status": "ERROR: insufficient funds to buy stock"}
        new_cents_total = int(cents) + cents_delta
        new_dollars_total = int(dollars) + dollars_delta
        if (new_cents_total < 0):
            new_dollars_total = new_dollars_total - 1
            new_cents_total = new_cents_total + 100
        elif (new_cents_total > 100):
            new_dollars_total = new_dollars_total + 1
            new_cents_total = new_cents_total - 100
        return {"status": "SUCCESS", "username": username, "dollars": new_dollars_total, "cents": new_cents_total}

    def set_trigger(self, trigger_type, username, stock_symbol, dollars, cents):
        assert type(trigger_type) == str
        if (trigger_type == TriggerTypes.BUY):
            triggers = json.loads(self.r.hget(username, "buy_triggers"))
        elif (trigger_type == TriggerTypes.SELL):
            json.loads(self.r.hget(username, "sell_triggers"))
        else:
            return {"status": f"ERROR: invalid trigger type, {trigger_type}"}
        triggers[stock_symbol] = {"dollars": dollars, "cents": cents}
        self.r.hset(username, trigger_type, json.dumps(triggers))
        return {"status": "SUCCESS", "username": username, trigger_type: triggers}