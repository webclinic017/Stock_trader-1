import redis
from user import user
import operator
import json
import time
redis_host = "127.0.0.1"
redis_port = 6379

def clear_db(r):
    r.execute_command("flushdb")

def createNewUser_noUserExists_newUserExistsInRedis(r, user_instance):
    clear_db(r)
    username = "user1"
    new_user = {b"stocks": b"{}", b"dollars": b"0", b"cents": b"0", b"buy_triggers": b"{}", b"sell_triggers": b"{}", b"buy_stack": b"[]", b"sell_stack": b"[]"}
    noResult = r.hgetall(username)
    user_instance.create_new_user(username)
    userResult = r.hgetall(username)
    assert(len(noResult) == 0)
    assert(len(userResult) > 0)
    assert(userResult == new_user)
    print("PASSED: createNewUser_noUserExists_newUserExistsInRedis")

def getUser_noUserExists_getsEmptyResult(r, user_instance):
    clear_db(r)
    userResult = user_instance.get_user("someImaginaryUser")
    assert(len(userResult) == 0)
    print("PASSED: getUser_noUserExists_getsEmptyUser")

def getUser_userExists_getsUser(r, user_instance):
    clear_db(r)
    username = "user1"
    some_user = {"stocks": "{}", "dollars": "0", "cents": "0", "buy_triggers": "{}", "sell_triggers": "{}", "buy_stack": "[]", "sell_stack": "[]"}
    user_instance.create_new_user(username)
    userResult = user_instance.get_user(username)
    assert(len(userResult) > 0)
    assert(userResult == some_user)
    print("PASSED: getUser_userExists_newUserExistsInRedis")

def addFundsDelta_add40Dollars30CentsToBrokeUser_userHas40DollarsAnd30CentsAddedToPreviousFunds(r, user_instance):
    clear_db(r)
    username = "user1"
    dollarsDelta = 40
    centsDelta = 30
    user_instance.create_new_user(username)
    userResultBefore = user_instance.get_user(username)
    user_instance.add_funds_delta(username, dollarsDelta, centsDelta)
    userResultPay1 = user_instance.get_user(username)
    user_instance.add_funds_delta(username, dollarsDelta, centsDelta)
    userResultPay2 = user_instance.get_user(username)

    assert(int(userResultBefore["dollars"]) == 0)
    assert(int(userResultBefore["cents"]) == 0)
    assert(int(userResultPay1["dollars"]) == dollarsDelta)
    assert(int(userResultPay1["cents"]) == centsDelta)
    assert(int(userResultPay2["dollars"]) == dollarsDelta * 2)
    assert(int(userResultPay2["cents"]) == centsDelta * 2)
    print("PASSED: addFundsDelta_add40Dollars30CentsToBrokeUser_userGetsTwoSuccessivePaymentsOf40Dollars30CentsAddedToFunds")

def pushCommand_2CommandsToPush_StackHas2PushedCommands(r, user_instance, command):
    clear_db(r)
    username = "user1"
    stack = f"{command}_stack"
    user_instance.create_new_user(username)
    user = user_instance.get_user(username)
    empty_stack = json.loads(user[stack])
    timestamp1 = time.time()
    user = user_instance.push_command(username=username, stock_symbol="STK_1", dollars=100, cents=20, command=command, timestamp=timestamp1)
    buy_stack_one_item = json.loads(user[stack])
    timestamp2 = time.time()
    user = user_instance.push_command(username=username, stock_symbol="STK_2", dollars=200, cents=30, command=command, timestamp=timestamp2)
    buy_stack_two_items = json.loads(user[stack])

    assert(len(empty_stack) == 0)
    assert(len(buy_stack_one_item) == 1)
    assert(len(buy_stack_two_items) == 2)
    assert(buy_stack_two_items[0] == {"stock_symbol": "STK_1", "dollars": 100, "cents": 20, "timestamp": timestamp1})
    assert(buy_stack_two_items[1] == {"stock_symbol": "STK_2", "dollars": 200, "cents": 30, "timestamp": timestamp2})
    print(f"PASSED: pushCommand_2CommandsToPush_StackHas2PushedCommands for {command} command")

def popCommand_2CommandsToPop_CorrectCommandsArePoppedInOrderOfLatestPush(r, user_instance, command):
    clear_db(r)
    username = "user1"
    user_instance.create_new_user(username)
    user_instance.get_user(username)
    timestamp1 = time.time()
    user_instance.push_command(username=username, stock_symbol="STK_1", dollars=100, cents=20, command=command, timestamp=timestamp1)
    timestamp2 = time.time()
    user_instance.push_command(username=username, stock_symbol="STK_2", dollars=200, cents=30, command=command, timestamp=timestamp2)

    item2 = user_instance.pop_command(username=username, command=command)
    item1 = user_instance.pop_command(username=username, command=command)

    assert(item1 == {"stock_symbol": "STK_1", "dollars": 100, "cents": 20, "timestamp": timestamp1})
    assert(item2 == {"stock_symbol": "STK_2", "dollars": 200, "cents": 30, "timestamp": timestamp2})
    print(f"PASSED: popCommand_2CommandsToPop_CorrectCommandsArePoppedInOrderOfLatestInsertion for {command} command")

def clearOldCommands_3StaleCommands2NewCommands_only2NewestCommandsRemain(r, user_instance, command):
    stack = f"{command}_stack"
    clear_db(r)
    username = "user1"
    user_instance.create_new_user(username)
    timestamp1 = time.time() - 60
    user_instance.push_command(username=username, stock_symbol="STK_1", dollars=100, cents=20, command=command, timestamp=timestamp1)
    timestamp2 = time.time() - 60
    user_instance.push_command(username=username, stock_symbol="STK_2", dollars=200, cents=30, command=command, timestamp=timestamp2)
    timestamp3 = time.time() - 60
    user_instance.push_command(username=username, stock_symbol="STK_3", dollars=300, cents=40, command=command, timestamp=timestamp3)
    timestamp4 = time.time()
    user_instance.push_command(username=username, stock_symbol="STK_4", dollars=400, cents=50, command=command, timestamp=timestamp4)
    timestamp5 = time.time()
    user_instance.push_command(username=username, stock_symbol="STK_5", dollars=500, cents=60, command=command, timestamp=timestamp5)
    
    stackBeforeClear = json.loads(user_instance.get_user(username)[stack])
    user_instance.clear_old_commands(username=username, command=command, current_time=time.time())
    stackAfterClear = json.loads(user_instance.get_user(username)[stack])
    assert(len(stackBeforeClear) == 5)
    assert(len(stackAfterClear) == 2)
    assert(stackAfterClear[0] == {"stock_symbol": "STK_4", "dollars": 400, "cents": 50, "timestamp": str(timestamp4)})
    assert(stackAfterClear[1] == {"stock_symbol": "STK_5", "dollars": 500, "cents": 60, "timestamp": str(timestamp5)})
    print(f"PASSED: clearOldCommands_3StaleCommands2NewCommands_only2NewestCommandsRemain for {command} command")

if __name__ == "__main__":
    print("\n--- user_tests ---")
    r = redis.Redis(host=redis_host, port=redis_port)
    user_instance = user(redis_host=redis_host, redis_port=redis_port)

    createNewUser_noUserExists_newUserExistsInRedis(r, user_instance)
    getUser_noUserExists_getsEmptyResult(r, user_instance)
    getUser_userExists_getsUser(r, user_instance)
    addFundsDelta_add40Dollars30CentsToBrokeUser_userHas40DollarsAnd30CentsAddedToPreviousFunds(r, user_instance)
    pushCommand_2CommandsToPush_StackHas2PushedCommands(r, user_instance, command="buy")
    popCommand_2CommandsToPop_CorrectCommandsArePoppedInOrderOfLatestPush(r, user_instance, command="buy")
    pushCommand_2CommandsToPush_StackHas2PushedCommands(r, user_instance, command="sell")
    popCommand_2CommandsToPop_CorrectCommandsArePoppedInOrderOfLatestPush(r, user_instance, command="sell")
    clearOldCommands_3StaleCommands2NewCommands_only2NewestCommandsRemain(r, user_instance, command="buy")
    clear_db(r)
    print("--------\n")