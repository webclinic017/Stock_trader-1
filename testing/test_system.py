import sys
import subprocess
import pytest
import requests
from enum_utils import CommandURLs

base_url = "http://127.0.0.1:5000"

# Usage:
#   1. Run start_script.py with a "--QuoteServer 0" flag
#   2. run 'pytest' from commandline within project directory

# Information:
#   - User funds are carried over between testing blocks
#   - Tests must be run on a freshly started system for a clear database until a reset system is created

# TODO: Test blocks should fully reset state before moving to next function test

# 'routes.main_page' testing ------------------------------------------------------------------------------------
def test_main_page_response_200_OK():
    server_response = requests.get((base_url + "/"))
    assert server_response.status_code == 200

# 'routes.displaySummary' testing 1-------------------------------------------------------------------------------
def test_displaySummary_response_200_OK():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    assert server_response.status_code == 200

def test_displaySummary_response_data():
    next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
    response_json = server_response.json()
    assert response_json["Command"] == "DISPLAY_SUMMARY"
    assert response_json["Data"]["Account"]["acc"] == 0
    assert not response_json["Data"]["Account"]["buy"]   # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]   # should be NO pending sells
    assert not response_json["Data"]["Account"]["stk"]   # should be NO stocks held
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.addFunds' testing -------------------------------------------------------------------------------------
def test_addFunds_response_200_OK():
    next_command = {"Command": "ADD", "userid": "j_doe", "amount": "5000.00"}
    server_response = requests.post((base_url + CommandURLs.ADD.value), data=next_command)
    assert server_response.status_code == 200

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
    assert response_json["Data"]["Account"]["acc"] == 10000.00
    assert not response_json["Data"]["Account"]["buy"]   # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]   # should be NO pending sells
    assert not response_json["Data"]["Account"]["stk"]   # should be NO stocks held
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.getQuote' testing -------------------------------------------------------------------------------------
def test_getQuote_response_200_OK():
    next_command = {"Command": "QUOTE", "userid": "j_doe", "StockSymbol": "ABC"}
    server_response = requests.post((base_url + CommandURLs.QUOTE.value), data=next_command)
    assert server_response.status_code == 200

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
    assert response_json["Data"]["Account"]["acc"] == 10000.00
    assert not response_json["Data"]["Account"]["buy"]   # should be NO pending buys
    assert not response_json["Data"]["Account"]["sel"]   # should be NO pending sells
    assert not response_json["Data"]["Account"]["stk"]   # should be NO stocks held
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.buyStock' testing -------------------------------------------------------------------------------------
def test_buyStock_response_200_OK():
    next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "ABC", "amount": "200.00"}
    server_response = requests.post((base_url + CommandURLs.BUY.value), data=next_command)
    assert server_response.status_code == 200

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
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.commitBuy' testing ------------------------------------------------------------------------------------
def test_commitBuy_response_200_OK():
    next_command = {"Command": "COMMIT_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_BUY.value), data=next_command)
    assert server_response.status_code == 200

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
    assert not response_json["Data"]["Triggers"]["buy"]     # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.cancelBuy' testing ------------------------------------------------------------------------------------
def test_cancelBuy_response_200_OK():
    next_command = {"Command": "CANCEL_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_BUY.value), data=next_command)
    assert server_response.status_code == 200

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
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.sellStock' testing ------------------------------------------------------------------------------------
def test_sellStock_response_200_OK():
    next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "ABC", "amount": "5"}
    server_response = requests.post((base_url + CommandURLs.SELL.value), data=next_command)
    assert server_response.status_code == 200

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
    assert not response_json["Data"]["Triggers"]["buy"]  # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]  # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.commitSell' testing -----------------------------------------------------------------------------------
def test_commitSell_response_200_OK():
    next_command = {"Command": "COMMIT_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_SELL.value), data=next_command)
    assert server_response.status_code == 200


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
    assert not response_json["Data"]["Triggers"]["buy"]     # should be NO buy triggers
    assert not response_json["Data"]["Triggers"]["sel"]     # should be NO sell triggers
    assert response_json["userid"] == "j_doe"

# 'routes.cancelSell' testing -----------------------------------------------------------------------------------
def test_cancelSell_response_200_OK():
    next_command = {"Command": "CANCEL_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SELL.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.setBuyAmount' testing ---------------------------------------------------------------------------------
def test_setBuyAmount_response_200_OK():
    next_command = {"Command": "SET_BUY_AMOUNT", "userid": "j_doe", "StockSymbol": "CBA", "amount": "150.00"}
    server_response = requests.post((base_url + CommandURLs.SET_BUY_AMOUNT.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.cancelSetBuy' testing ---------------------------------------------------------------------------------
def test_cancelSetBuy_response_200_OK():
    next_command = {"Command": "CANCEL_SET_BUY", "userid": "j_doe", "StockSymbol": "CBA"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SET_BUY.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.setBuyTrigger' testing --------------------------------------------------------------------------------
def test_setBuyTrigger_response_200_OK():
    next_command = {"Command": "SET_BUY_TRIGGER", "userid": "j_doe", "StockSymbol": "CAB", "amount": "15.00"}
    server_response = requests.post((base_url + CommandURLs.SET_BUY_TRIGGER.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.setSellAmount' testing --------------------------------------------------------------------------------
def test_setSellAmount_response_200_OK():
    next_command = {"Command": "SET_SELL_AMOUNT", "userid": "j_doe", "StockSymbol": "ABC", "amount": "5"}
    server_response = requests.post((base_url + CommandURLs.SET_SELL_AMOUNT.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.cancelSetSell' testing --------------------------------------------------------------------------------
def test_cancelSetSell_response_200_OK():
    next_command = {"Command": "CANCEL_SET_SELL", "userid": "j_doe", "StockSymbol": "ABC"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SET_SELL.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.setSellTrigger' testing -------------------------------------------------------------------------------
def test_setSellTrigger_response_200_OK():
    next_command = {"Command": "SET_SELL_TRIGGER", "userid": "j_doe", "StockSymbol": "ABC", "amount": "150.00"}
    server_response = requests.post((base_url + CommandURLs.SET_SELL_TRIGGER.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.dumpLog[user]' testing --------------------------------------------------------------------------------
def test_dumpLog_user_response_200_OK():
    next_command = {"Command": "DUMPLOG", "userid": "j_doe", "filename": "user_dumplog_test.txt"}
    server_response = requests.post((base_url + CommandURLs.DUMPLOG.value), data=next_command)
    assert server_response.status_code == 200

# TODO: Test the dumplogs against xml schema
# TODO: Ensure proper logs are submitted for each transaction

# 'routes.dumpLog[admin]' testing -------------------------------------------------------------------------------
def test_dumpLog_admin_response_200_OK():
    next_command = {"Command": "DUMPLOG", "filename": "admin_dumplog_test.txt"}
    server_response = requests.post((base_url + CommandURLs.DUMPLOG.value), data=next_command)
    assert server_response.status_code == 200

# TODO: Test the dumplogs against xml schema
# TODO: Ensure proper logs are submitted for each transaction
# ----------------------------------
