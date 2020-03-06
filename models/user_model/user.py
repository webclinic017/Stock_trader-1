import redis
import json
import threading
from heapq import heappop, heappush
class Resource:
    STOCK_DELTA = "stock_delta"
    ADD_FUNDS_DELTA = "add_funds_delta"
    SET_TRIGGER = "set_trigger"
    COMMAND_STACK = "command_stack"

class user:
    class TriggerTypes:
        BUY = "buy_triggers"
        SELL = "sell_triggers"
        
    def __init__(self, redis_host, redis_port):
        self.r = redis.Redis(host=redis_host, port=redis_port)
        self.resources = {
            Resource.STOCK_DELTA: {},
            Resource.ADD_FUNDS_DELTA: {},
            Resource.SET_TRIGGER: {},
            Resource.COMMAND_STACK: {}
        }

    def _lock(self, resource, username):
        mutex = self._get_mutex(resource, username)
        mutex.acquire()
        return mutex

    def _get_mutex(self, resource, username):
        resource_dict = self.resources[resource]
        try:
            mutex = resource_dict[username]
        except KeyError:
            mutex = threading.Lock()
            self.resources[resource][username] = mutex
        return mutex

    def _sanitize(self, input):
        sanitized_input = {}
        if (type(input) == list):
            sanitized_input = [self._sanitize(item) for item in input]
        elif(type(input) == bytes):
            sanitized_input = self._sanitize(str(input, encoding="utf-8"))
        elif (type(input) == str):
            sanitized_input = self._sanitize(json.loads(input))
        elif (type(input) == dict):
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
                    val_str = val
                elif (type(val) == bytes):
                    val_str = str(val, encoding="utf-8")
                else:
                    val_str = str(val)
                sanitized_input[key_str] = val_str
        else: # input is some json parseable primitive
            sanitized_input = input
        return sanitized_input

    def create_new_user(self, username):
        empty_user = {"stocks": "{}", "dollars": 0, "cents": 0, "buy_triggers": "{}", "sell_triggers": "{}", "buy_stack": "[]", "sell_stack": "[]"}
        success = self.r.hmset(username, empty_user)
        empty_user["username"] = username
        return empty_user

    def get_user(self, username):
        result = self._sanitize(self.r.hgetall(username))
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
            stocks = self.r.hget(username, "stocks")
            all_stocks = self._sanitize(stocks)
            num_stocks_for_symbol = all_stocks[stock_symbol]
            print("all stocks")
            print(all_stocks)
            print(f"number of {stock_symbol} stocks:")
            print(num_stocks_for_symbol)
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
        mutex = self._lock(Resource.STOCK_DELTA, username)
        try:
            amount_delta = dollars_delta + (cents_delta / 100)
            stock_price = (stock_price_dollars + (stock_price_cents / 100))
            stock_delta_value = int(amount_delta / stock_price)
            stocks = json.loads(self.r.hget(username, "stocks"))
            if (stock_symbol == "stock_symbol"):
                raise Exception("stock_symbol key equals 'stock_symbol'")
            try:
                number_of_stock = stocks[stock_symbol]
            except KeyError:
                stocks[stock_symbol] = 0
                number_of_stock = stocks[stock_symbol]
            new_stock_amount = number_of_stock + stock_delta_value 
            if (new_stock_amount < 0): # invalid condition
                raise Exception(f"{username} has insufficient number of {stock_symbol} stocks ({number_of_stock}) to sell")
            stocks[stock_symbol] = new_stock_amount
            stocks_str = json.dumps(stocks)
            updated_funds = self.add_funds_delta(username, dollars_delta, cents_delta, persist=False) # do not persist yet, because need to ensure updated_funds >= 0
            if (updated_funds["dollars"] < 0 or updated_funds["cents"] < 0):
                raise Exception(f"{username} has negative funds after applying ${dollars_delta}.{abs(cents_delta)} delta.")
            self.r.hmset(username, {"dollars": updated_funds["dollars"], "cents": updated_funds["cents"], "stocks": stocks_str})
            response = updated_funds
            response["stocks"] = stocks_str
        except Exception as e:
            print(e)
            response = {}
            response["stocks"] = "{}"
            response["status"] = "ERROR"
            response["message"] = str(e)
        finally:
            mutex.release()
        return response

    def add_funds_delta(self, username, dollars_delta, cents_delta, persist=True):
        mutex = self._lock(Resource.ADD_FUNDS_DELTA, username)
        try:
            funds_delta = dollars_delta + (cents_delta / 100)
            user = self._sanitize(self.r.hgetall(username))
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
            mutex.release()

        return {"status": "SUCCESS", "username": username, "dollars": new_dollars_total, "cents": new_cents_total}

    def set_trigger(self, trigger_type, username, stock_symbol, dollars, cents):
        assert type(trigger_type) == str
        mutex = self._lock(Resource.SET_TRIGGER, username)
        try:
            if (trigger_type == TriggerTypes.BUY):
                triggers = json.loads(self.r.hget(username, "buy_triggers"))
            elif (trigger_type == TriggerTypes.SELL):
                triggers = json.loads(self._sanitize(self.r.hget(username, "sell_triggers")))
            else:
                return {"status": f"ERROR: invalid trigger type, {trigger_type}"}
            triggers[stock_symbol] = {"dollars": dollars, "cents": cents}

            self.r.hset(username, trigger_type, json.dumps(triggers))
        finally:
            mutex.release()
        return {"status": "SUCCESS", "username": username, trigger_type: triggers}

    def push_command(self, username, stock_symbol, dollars, cents, command, timestamp):
        key = f"{command}_stack"
        mutex = self._lock(Resource.COMMAND_STACK, username)
        try:
            user = self.get_user(username)
            command_stack = json.loads(user[key])
            item = {"stock_symbol": stock_symbol, "dollars": dollars, "cents": cents, "timestamp": timestamp}
            command_stack.append(item)
            command_stack_str = json.dumps(command_stack)
            print("push:")
            print(item)
            self.r.hset(username, key, command_stack_str)
            print("command stack result:")
            print(command_stack_str)
            user[key] = command_stack_str
        finally:
            mutex.release()
        return user

    def pop_command(self, username, command):
        key = f"{command}_stack"
        mutex = self._lock(Resource.COMMAND_STACK, username)
        try:
            user = self.get_user(username)
            command_stack = json.loads(user[key])
            print("command stack: ")
            print(command_stack)
            #command_stack = self._order_by_timestamp(json.loads(user[key]))

            try:
                popped_item = command_stack.pop()
                self.r.hset(username, key, json.dumps(command_stack))
            except IndexError:
                popped_item = {}
                pass
        finally:
            mutex.release()
        return popped_item

    def clear_old_commands(self, username, command, current_time):
        print("clear old commands")
        response = {"status": "Success"}
        key = f"{command}_stack"
        mutex = self._lock(Resource.COMMAND_STACK, username)
        try:
            result = self.r.hget(username, key)
            stack = self._sanitize(result)
            cleared_stack = []
            try:
                for i in range(len(stack)):
                    item = stack[i]
                    try:
                        if (int(float(current_time)) - int(float(item["timestamp"])) < 60):
                            item["dollars"] = int(item["dollars"])
                            item["cents"] = int(item["cents"])
                            cleared_stack.append(item)
                    except ValueError:
                        pass
                self.r.hset(username, key, json.dumps(cleared_stack))
            except Exception as e:
                print(e)
                response["status"] = "ERROR"
                response["message"] = str(e)
        finally:
            mutex.release()
        return response

    def _order_by_timestamp(self, records):
        assert type(records) == list
        sorted_records = []
        if (len(records) > 0):
            assert type(records[0]["timestamp"]) == str
            for record in records:
                timestamp = int(float(record["timestamp"]) * 10000000)
                heappush(sorted_records, (timestamp, record))
        return sorted_records
