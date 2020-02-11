import sys
import requests
from enum_utils import CommandURLs

base_url = "http://127.0.0.1:5000"


# 'routes.main_page' testing
def test_main_page_response_200_OK():
    server_response = requests.get((base_url + "/"))
    assert server_response.status_code == 200

# 'routes.addFunds' testing
def test_addFunds_response_200_OK():
    next_command = {"Command": "ADD", "userid": "j_doe", "amount": "5000.00"}
    server_response = requests.post((base_url + CommandURLs.ADD.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.getQuote' testing
def test_getQuote_response_200_OK():
    next_command = {"Command": "QUOTE", "userid": "j_doe", "StockSymbol": "ABC"}
    server_response = requests.post((base_url + CommandURLs.QUOTE.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.buyStock' testing
def test_buyStock_response_200_OK():
    next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "ABC", "amount": "200.00"}
    server_response = requests.post((base_url + CommandURLs.BUY.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.commitBuy' testing
def test_commitBuy_response_200_OK():
    next_command = {"Command": "COMMIT_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_BUY.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.cancelBuy' testing
def test_cancelBuy_response_200_OK():
    next_command = {"Command": "CANCEL_BUY", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_BUY.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.sellStock' testing
def test_sellStock_response_200_OK():
    next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "ABC", "amount": "5"}
    server_response = requests.post((base_url + CommandURLs.SELL.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.commitSell' testing
def test_commitSell_response_200_OK():
    next_command = {"Command": "COMMIT_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.COMMIT_SELL.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.cancelSell' testing
def test_cancelSell_response_200_OK():
    next_command = {"Command": "CANCEL_SELL", "userid": "j_doe"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SELL.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.setBuyAmount' testing
def test_setBuyAmount_response_200_OK():
    next_command = {"Command": "SET_BUY_AMOUNT", "userid": "j_doe", "StockSymbol": "CBA", "amount": "150.00"}
    server_response = requests.post((base_url + CommandURLs.SET_BUY_AMOUNT.value), data=next_command)
    assert server_response.status_code == 200

# 'routes.cancelSetBuy' testing
def cancelSetBuy():
    next_command = {"Command": "CANCEL_SET_BUY", "userid": "j_doe", "StockSymbol": "CBA"}
    server_response = requests.post((base_url + CommandURLs.CANCEL_SET_BUY.value), data=next_command)
    assert server_response.status_code == 200
# ----------------------------------

