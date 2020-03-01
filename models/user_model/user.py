import redis
import json
import threading
class user:
    class TriggerTypes:
        BUY = "buy_triggers"
        SELL = "sell_triggers"
    def __init__(self, redis_host, redis_port):
        self.r = redis.Redis(host=redis_host, port=redis_port)
        self.stock_delta_mutex = threading.Lock()
        self.set_trigger_mutex = threading.Lock()
        self.add_funds_delta_mutex = threading.Lock()

    def _sanitize_byte_keys_and_vals(self, input):
        sanitized_dict = {}
        if (not (type(input) == dict)):
            result_dict = json.loads(input)
        else:
            input_dict = input.copy()
            keys = input_dict.keys()
            for key in keys:
                if (type(key) == str):
                    key_str = key
                elif(type(key) == int):
                    key_str = str(key)
                else:
                    key_str = str(key, encoding="utf-8")
                try:
                    val = input_dict[key_str]
                except KeyError:
                    val = input_dict[key]
                if (type(val) == str):
                    val_str = key
                else:
                    val_str = str(val, encoding="utf-8")
                sanitized_dict[key_str] = val_str
            result_dict = sanitized_dict
        return result_dict

    def push_command(self, username, stock_symbol, dollars, cents, command, timestamp):
        key = f"{command}_stack"
        user = self.get_user(username)
        command_stack = json.loads(user[key])
        command_stack.append({"stock_symbol": stock_symbol, "dollars": dollars, "cents": cents})
        command_stack_str = json.dumps(command_stack)
        self.r.hset(username, key, command_stack_str)
        user[key] = command_stack_str
        return user

    def pop_command(self, username, command):
        key = f"{command}_stack"
        user = self.get_user(username)
        command_stack = json.loads(user[key])
        popped_item = command_stack.pop()
        self.r.hset(username, key, json.dumps(command_stack))
        return popped_item

    def create_new_user(self, username):
        empty_user = {"stocks": "{}", "dollars": 0, "cents": 0, "buy_triggers": "{}", "sell_triggers": "{}", "buy_stack": "[]", "sell_stack": "[]"}
        success = self.r.hmset(username, empty_user)
        empty_user["username"] = username
        return empty_user

    def get_user(self, username):
        result = self._sanitize_byte_keys_and_vals(self.r.hgetall(username))
        return result

    def user_funds(self, username):
        user = self.get_user(username)
        try:
            dollars = user["dollars"]
            cents = user["cents"]
        except KeyError:
            dollars = 0
            cents = 0
        return {"username": username, "dollars": dollars, "cents": cents}

    def number_of_stocks(self, username, stock_symbol):
        try:
            all_stocks = self._sanitize_byte_keys_and_vals(self.r.hget(username, "stocks"))
            num_stocks_for_symbol = all_stocks[stock_symbol]
        except KeyError:
            num_stocks_for_symbol = 0
        return num_stocks_for_symbol

    def stock_delta(self, 
                    username, 
                    stock_symbol, 
                    stock_price_dollars, 
                    stock_price_cents, 
                    dollars_delta, 
                    cents_delta):
        self.stock_delta_mutex.acquire()
        try:
            try:
                updated_funds = self.add_funds_delta(username, dollars_delta, cents_delta, persist=False)
                #if (updated_funds["status"] != "SUCCESS"):
                #    response = updated_funds
                #    return response
                amount_delta = dollars_delta + (cents_delta / 100)
                stock_price = (stock_price_dollars + (stock_price_cents / 100))
                stock_delta_value = int(amount_delta / stock_price)
                stocks = json.loads(self.r.hget(username, "stocks"))
                stocks[stock_symbol] = stocks[stock_symbol] + stock_delta_value
            except KeyError: # condition where the user doesn't own any stock for this symbol
                if (stock_delta_value < 0): # sell condition
                    return {"username": username, f"status": "ERROR: insufficient number of {stock_symbol} stock to sell"} # error if intent is to sell
                stocks[stock_symbol] = stock_delta_value # add number of stock as new symbol entry if intent is to buy
            stocks_str = json.dumps(stocks)
            self.r.hmset(username, {"dollars": updated_funds["dollars"], "cents": updated_funds["cents"], "stocks": stocks_str})
        finally:
            self.stock_delta_mutex.release()
        response = updated_funds
        response["stocks"] = stocks_str
        return response

    def add_funds_delta(self, username, dollars_delta, cents_delta, persist=True):
        self.add_funds_delta_mutex.acquire()
        try:
            funds_delta = dollars_delta + (cents_delta / 100)
            user = self._sanitize_byte_keys_and_vals(self.r.hgetall(username))
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
            if (persist):
                self.r.hmset(username, {"dollars": new_dollars_total, "cents": new_cents_total})
        except KeyError: # condition where get_user() returns empty dict, when there is no user account to add the funds to. If persist flag is set, then want to create new user then
            if (persist):
                self.create_new_user(username)
                self.r.hmset(username, {"dollars": dollars_delta, "cents": cents_delta})
            new_dollars_total = dollars_delta
            new_cents_total = cents_delta
        finally:
            self.add_funds_delta_mutex.release()

        return {"status": "SUCCESS", "username": username, "dollars": new_dollars_total, "cents": new_cents_total}

    def set_trigger(self, trigger_type, username, stock_symbol, dollars, cents):
        assert type(trigger_type) == str
        self.set_trigger_mutex.acquire()
        try:
            if (trigger_type == TriggerTypes.BUY):
                triggers = json.loads(self.r.hget(username, "buy_triggers"))
            elif (trigger_type == TriggerTypes.SELL):
                triggers = json.loads(self._sanitize_byte_keys_and_vals(self.r.hget(username, "sell_triggers")))
            else:
                return {"status": f"ERROR: invalid trigger type, {trigger_type}"}
            triggers[stock_symbol] = {"dollars": dollars, "cents": cents}

            self.r.hset(username, trigger_type, json.dumps(triggers))
        finally:
            self.set_trigger_mutex.release()
        return {"status": "SUCCESS", "username": username, trigger_type: triggers}