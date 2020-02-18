import sys
import subprocess
import pytest
import requests
from enum_utils import CommandURLs

base_url = "http://127.0.0.1:5000"

# Usage:
#   1. Run start_script.py with a "--QuoteServer 0" flag
#   2. run 'pytest' from commandline within project directory to run all project tests
#       - run 'pytest test_system.py' to run just this file
#       - run 'pytest test_system.py::specific_test_name' to run just one test in this file

# Information:
#   - User funds are carried over between testing blocks
#   - Tests must be run on a freshly started system for a clear database until a reset system is created

# TODO: Test blocks should fully reset state before moving to next function test

@pytest.fixture
def set_funds():
    next_command = {"Command": "ADD", "userid": "j_doe", "amount": "5000.00"}
    requests.post((base_url + CommandURLs.ADD.value), data=next_command)

# 'main_page' testing --------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_main_page_response_200_OK():
    server_response = requests.get((base_url + "/"))
    assert server_response.status_code == 200

# 'displaySummary' testing 1--------------------------------------------------------------------------------------------
# =====web server response check=====
def test_displaySummary_response_200_OK():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_displaySummary_response_data():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 0  # should have no funds
    assert not response_json["Data"]["Account"]["buy"]   # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]   # should be NO pending sells
    assert not response_json["Data"]["Account"]["stk"]   # should be NO stocks held
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'addFunds' testing ---------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_addFunds_response_200_OK():
    next_command = {"Command": "ADD", "userid": "j_doe", "amount": "5000.00"}
    server_response = requests.post((base_url + CommandURLs.ADD.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_addFunds_response_data():
    next_command = {"Command": "ADD", "userid": "j_doe", "amount": "5000.00"}
    server_response = requests.post((base_url + CommandURLs.ADD.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "ADD"
    assert response_json["Succeeded"]
    assert response_json["amount"] == "5000.00"
    assert response_json["userid"] == "j_doe"

def test_post_addFunds_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 10000.00  # should have 10000.00 in funds
    assert not response_json["Data"]["Account"]["buy"]   # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]   # should be NO pending sells
    assert not response_json["Data"]["Account"]["stk"]   # should be NO stocks held
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'getQuote' testing ---------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_getQuote_response_200_OK():
    next_command = {"Command": "QUOTE", "userid": "j_doe", "StockSymbol": "ABC"}
    server_response = requests.post((base_url + CommandURLs.QUOTE.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_getQuote_response_data():
    next_command = {"Command": "QUOTE", "userid": "j_doe", "StockSymbol": "ABC"}
    server_response = requests.post((base_url + CommandURLs.QUOTE.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "QUOTE"
    assert response_json["Quote"] == 20.87
    assert response_json["StockSymbol"] == "ABC"
    assert response_json["Succeeded"][0] == 20.87
    assert response_json["Succeeded"][1] == "ABC"
    assert response_json["Succeeded"][2] == "j_doe"
    assert response_json["userid"] == "j_doe"

def test_post_getQuote_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 10000.00  # should have 10000.00 in funds
    assert not response_json["Data"]["Account"]["buy"]   # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]   # should be NO pending sells
    assert not response_json["Data"]["Account"]["stk"]   # should be NO stocks held
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'buyStock' testing ---------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_buyStock_response_200_OK():
    next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "ABC", "amount": "200.00"}
    server_response = requests.post((base_url + CommandURLs.BUY.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_buyStock_response_data():
    next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "ABC", "amount": "115.37"}
    server_response = requests.post((base_url + CommandURLs.BUY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "BUY"
    assert response_json["StockSymbol"] == "ABC"
    assert response_json["Succeeded"]
    assert response_json["amount"] == "115.37"
    assert response_json["userid"] == "j_doe"

def test_post_buyStock_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 10000.00  # no funds should be removed until commit
    assert len(response_json["Data"]["Account"]["buy"]) == 1    # should only be 1 pending buy
    assert response_json["Data"]["Account"]["buy"][0][0] == "ABC"
    assert response_json["Data"]["Account"]["buy"][0][1] == 115.37
    assert not response_json["Data"]["Account"]["sel"]   # should be NO pending buys
    assert not response_json["Data"]["Account"]["stk"]   # should be NO stocks held
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'commitBuy' testing --------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_commitBuy_response_200_OK():
    next_command = {"Command": "COMMIT_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_BUY.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_commitBuy_response_data_fail():
    next_command = {"Command": "COMMIT_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_BUY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "COMMIT_BUY"
    assert not response_json["Succeeded"]   # should be NO pending buys
    assert response_json["userid"] == "j_doe"

def test_commitBuy_response_data_pass():
    # Send buy command
    next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "ABC", "amount": "200.00"}
    requests.post((base_url + CommandURLs.BUY.value), data=next_command)
    # Commit buy command
    next_command = {"Command": "COMMIT_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_BUY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "COMMIT_BUY"
    assert response_json["Succeeded"]
    assert response_json["userid"] == "j_doe"

def test_post_commitBuy_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 9707.82
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 14}
    assert not response_json["Data"]["Triggers"]["buy"]     # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'cancelBuy' testing --------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_cancelBuy_response_200_OK():
    next_command = {"Command": "CANCEL_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_BUY.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_cancelBuy_response_data_fail():
    next_command = {"Command": "CANCEL_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_BUY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "CANCEL_BUY"
    assert not response_json["Succeeded"]       # should be NO pending buys
    assert response_json["userid"] == "j_doe"

def test_cancelBuy_response_data_pass():
    # Send buy command
    next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "BAC", "amount": "200.00"}
    requests.post((base_url + CommandURLs.BUY.value), data=next_command)
    # Cancel buy command
    next_command = {"Command": "CANCEL_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_BUY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "CANCEL_BUY"
    assert response_json["Succeeded"]
    assert response_json["userid"] == "j_doe"

def test_post_cancelBuy_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Data"]["Account"]["acc"] == 9707.82
    assert not response_json["Data"]["Account"]["buy"]  # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]  # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 14}
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'sellStock' testing --------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_sellStock_response_200_OK():
    next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "ABC", "amount": "5"}
    server_response = requests.post((base_url + CommandURLs.SELL.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_sellStock_response_data_pass():
    next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "ABC", "amount": "210.00"}
    server_response = requests.post((base_url + CommandURLs.SELL.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "SELL"
    assert response_json["StockSymbol"] == "ABC"
    assert response_json["Succeeded"]
    assert response_json["amount"] == "210.00"
    assert response_json["userid"] == "j_doe"

def test_sellStock_response_data_fail():
    next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "ABC", "amount": "5000.00"}
    server_response = requests.post((base_url + CommandURLs.SELL.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "SELL"
    assert response_json["StockSymbol"] == "ABC"
    assert not response_json["Succeeded"]   # user shouldn't have enough stock for 'sell' to be pending
    assert response_json["amount"] == "5000.00"
    assert response_json["userid"] == "j_doe"

def test_post_sellStock_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 9707.82
    assert not response_json["Data"]["Account"]["buy"]         # should be NO pending buys
    assert len(response_json["Data"]["Account"]["sel"]) == 1   # should only be 1 pending sell(2nd overwrites 1st)
    assert response_json["Data"]["Account"]["sel"][0][0] == "ABC"
    assert response_json["Data"]["Account"]["sel"][0][1][0] == 210.00
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 14}  # No stock should be removed yet
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'commitSell' testing -------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_commitSell_response_200_OK():
    next_command = {"Command": "COMMIT_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_SELL.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_commitSell_response_data_fail():
    next_command = {"Command": "COMMIT_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_SELL.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "COMMIT_SELL"
    assert not response_json["Succeeded"]   # should be NO pending sells
    assert response_json["userid"] == "j_doe"

def test_commitSell_response_data_pass():
    # Send sell command
    next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "ABC", "amount": "63.00"}
    requests.post((base_url + CommandURLs.SELL.value), data=next_command)
    # Commit sell command
    next_command = {"Command": "COMMIT_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_SELL.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "COMMIT_SELL"
    assert response_json["Succeeded"]
    assert response_json["userid"] == "j_doe"

def test_post_commitSell_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 9979.13
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1}
    assert not response_json["Data"]["Triggers"]["buy"]     # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'cancelSell' testing -------------------------------------------------------------------------------------------------
# =====web server response check=====
def test_cancelSell_response_200_OK():
    next_command = {"Command": "CANCEL_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SELL.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_cancelSell_response_data_fail():
    next_command = {"Command": "CANCEL_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SELL.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "CANCEL_SELL"
    assert not response_json["Succeeded"]   # should be NO pending sells
    assert response_json["userid"] == "j_doe"

def test_cancelSell_response_data_pass():
    # Send buy command
    next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "BAC", "amount": "2000.00"}
    requests.post((base_url + CommandURLs.BUY.value), data=next_command)
    # Commit buy command
    next_command = {"Command": "COMMIT_BUY", "userid": "j_doe"}
    requests.post((base_url + CommandURLs.COMMIT_BUY.value), data=next_command)
    # Send sell command
    next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "BAC", "amount": "84.00"}
    requests.post((base_url + CommandURLs.SELL.value), data=next_command)
    # Commit sell command
    next_command = {"Command": "CANCEL_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SELL.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "CANCEL_SELL"
    assert response_json["Succeeded"]
    assert response_json["userid"] == "j_doe"

def test_post_cancelSell_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}
    assert not response_json["Data"]["Triggers"]["buy"]     # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'setBuyAmount' testing -----------------------------------------------------------------------------------------------
# =====web server response check=====
def test_setBuyAmount_response_200_OK():
    next_command = {"Command": "SET_BUY_AMOUNT", "userid": "j_doe", "StockSymbol": "CBA", "amount": "150.00"}
    server_response = requests.post((base_url + CommandURLs.SET_BUY_AMOUNT.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_post_setBuyAmount_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7846.48
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}
    assert response_json["Data"]["Triggers"]["buy"] == {"CBA": "[None, 150.0, 0]"}  # should be 1 buy amount set
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'cancelSetBuy' testing -----------------------------------------------------------------------------------------------
# =====web server response check=====
def test_cancelSetBuy_response_200_OK():
    next_command = {"Command": "CANCEL_SET_BUY", "userid": "j_doe", "StockSymbol": "CBA"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SET_BUY.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_post_cancelSetBuy_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}
    assert response_json["Data"]["Triggers"]["buy"] == {}   # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

def test_post_cancelSetBuy_nothing_set():
    # Send a cancel set buy for a non-existent stock
    next_command = {"Command": "CANCEL_SET_BUY", "userid": "j_doe", "StockSymbol": "AAA"}
    requests.post((base_url + CommandURLs.CANCEL_SET_BUY.value), data=next_command)
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}
    assert response_json["Data"]["Triggers"]["buy"] == {}   # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

# 'setBuyTrigger' testing ----------------------------------------------------------------------------------------------
# =====web server response check=====
def test_setBuyTrigger_response_200_OK():
    next_command = {"Command": "SET_BUY_TRIGGER", "userid": "j_doe", "StockSymbol": "CAB", "amount": "15.00"}
    server_response = requests.post((base_url + CommandURLs.SET_BUY_TRIGGER.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_post_setBuyTrigger_fail_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}
    assert response_json["Data"]["Triggers"]["buy"] == {}   # should be NO buy amounts/triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

def test_post_setBuyTrigger_pass_user_state():
    next_command = {"Command": "SET_BUY_AMOUNT", "userid": "j_doe", "StockSymbol": "FTA", "amount": "253.15"}
    requests.post((base_url + CommandURLs.SET_BUY_AMOUNT.value), data=next_command)
    next_command = {"Command": "SET_BUY_TRIGGER", "userid": "j_doe", "StockSymbol": "FTA", "amount": "20.00"}
    requests.post((base_url + CommandURLs.SET_BUY_TRIGGER.value), data=next_command)
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7743.33
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}
    assert response_json["Data"]["Triggers"]["buy"] == {"FTA": "[active, 253.15, 20.0]"}  # should be 1 active buy trigger
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"
    # Send a cancel set buy to clear triggers
    next_command = {"Command": "CANCEL_SET_BUY", "userid": "j_doe", "StockSymbol": "FTA"}
    requests.post((base_url + CommandURLs.CANCEL_SET_BUY.value), data=next_command)

# 'setSellAmount' testing ----------------------------------------------------------------------------------------------
# =====web server response check=====
def test_setSellAmount_response_200_OK():
    next_command = {"Command": "SET_SELL_AMOUNT", "userid": "j_doe", "StockSymbol": "BAC", "amount": "50"}
    server_response = requests.post((base_url + CommandURLs.SET_SELL_AMOUNT.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_post_setSellAmount_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48   # NO fund changes for set sell amount
    assert not response_json["Data"]["Account"]["buy"]          # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]          # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 45}  # stock reserved for given set sell symbol
    assert response_json["Data"]["Triggers"]["buy"] == {}       # should be NO buy amounts/triggers
    assert response_json["Data"]["Triggers"]["sel"] == {"BAC": "[None, 50, 0]"}  # should be 1 sell amount
    assert response_json["userid"] == "j_doe"

# 'cancelSetSell' testing ----------------------------------------------------------------------------------------------
# =====web server response check=====
def test_cancelSetSell_response_200_OK():
    next_command = {"Command": "CANCEL_SET_SELL", "userid": "j_doe", "StockSymbol": "BAC"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SET_SELL.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_post_cancelSetSell_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48   # NO fund changes for set sell amount
    assert not response_json["Data"]["Account"]["buy"]          # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]          # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}  # stock reserved for given set sell symbol
    assert response_json["Data"]["Triggers"]["buy"] == {}       # should be NO buy amounts/triggers
    assert response_json["Data"]["Triggers"]["sel"] == {}       # should be NO sell amount
    assert response_json["userid"] == "j_doe"

# 'setSellTrigger' testing ---------------------------------------------------------------------------------------------
# =====web server response check=====
def test_setSellTrigger_response_200_OK():
    next_command = {"Command": "SET_SELL_TRIGGER", "userid": "j_doe", "StockSymbol": "ABC", "amount": "20.00"}
    server_response = requests.post((base_url + CommandURLs.SET_SELL_TRIGGER.value), data=next_command)
    assert server_response.status_code == 200

# =====transaction server response checks=====
def test_post_setSellTrigger_fail_user_state():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48  # NO fund changes for set sell amount
    assert not response_json["Data"]["Account"]["buy"]         # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]         # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 95}
    assert response_json["Data"]["Triggers"]["buy"] == {}      # should be NO buy amounts/triggers
    assert response_json["Data"]["Triggers"]["sel"] == {}      # should be NO sell amounts/triggers
    assert response_json["userid"] == "j_doe"

def test_post_setSellTrigger_pass_user_state():
    next_command = {"Command": "SET_SELL_AMOUNT", "userid": "j_doe", "StockSymbol": "BAC", "amount": "34"}
    requests.post((base_url + CommandURLs.SET_SELL_AMOUNT.value), data=next_command)
    next_command = {"Command": "SET_SELL_TRIGGER", "userid": "j_doe", "StockSymbol": "BAC", "amount": "21.00"}
    requests.post((base_url + CommandURLs.SET_SELL_TRIGGER.value), data=next_command)
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 7996.48
    assert not response_json["Data"]["Account"]["buy"]      # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]      # should be NO pending sells
    assert response_json["Data"]["Account"]["stk"] == {"ABC": 1, "BAC": 61}
    assert response_json["Data"]["Triggers"]["buy"] == {}   # should be NO buy amounts/triggers
    assert response_json["Data"]["Triggers"]["sel"] == {"BAC": "[active, 34, 21.0]"}  # should be 1 active sell trigger
    assert response_json["userid"] == "j_doe"

# 'dumpLog[user]' testing ----------------------------------------------------------------------------------------------
# =====web server response check=====
def test_dumpLog_user_response_200_OK():
    next_command = {"Command": "DUMPLOG", "userid": "j_doe", "filename": "user_dumplog_test.txt"}
    server_response = requests.post((base_url + CommandURLs.DUMPLOG.value), data=next_command)
    assert server_response.status_code == 200

# TODO: Test the dumplogs against xml schema
# TODO: Ensure proper logs are submitted for each transaction

# 'dumpLog[admin]' testing ---------------------------------------------------------------------------------------------
# =====web server response check=====
def test_dumpLog_admin_response_200_OK():
    next_command = {"Command": "DUMPLOG", "filename": "admin_dumplog_test.txt"}
    server_response = requests.post((base_url + CommandURLs.DUMPLOG.value), data=next_command)
    assert server_response.status_code == 200

# TODO: Test the dumplogs against xml schema
# TODO: Ensure proper logs are submitted for each transaction
# ----------------------------------
