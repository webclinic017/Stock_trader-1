import redis
from user import user
import operator
redis_host = "127.0.0.1"
redis_port = "6379"

def clear_db(r):
    r.execute_command("flushdb")

def createNewUser_noUserExists_newUserExistsInRedis(r, user_instance):
    clear_db(r)
    username = "user1"
    new_user = {b"stocks": b"{}", b"dollars": b"0", b"cents": b"0", b"buy_triggers": b"{}", b"sell_triggers": b"{}"}
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
    some_user = {"stocks": "{}", "dollars": "0", "cents": "0", "buy_triggers": "{}", "sell_triggers": "{}"}
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


if __name__ == "__main__":
    print("\n--- user_tests ---")
    r = redis.Redis(host=redis_host, port=redis_port)
    user_instance = user(redis_host=redis_host, redis_port=redis_port)

    createNewUser_noUserExists_newUserExistsInRedis(r, user_instance)
    getUser_noUserExists_getsEmptyResult(r, user_instance)
    getUser_userExists_getsUser(r, user_instance)
    addFundsDelta_add40Dollars30CentsToBrokeUser_userHas40DollarsAnd30CentsAddedToPreviousFunds(r, user_instance)
    clear_db(r)
    print("--------\n")