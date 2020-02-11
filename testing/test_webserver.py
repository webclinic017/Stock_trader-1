import sys
import subprocess
import pytest
import requests
from enum_utils import CommandURLs

base_url = "http://127.0.0.1:5000"
subprocesses = []

def start_service(path_to_entrypoint, script_args=[]):
    python_executable = sys.executable
    p_args = [python_executable, path_to_entrypoint]
    for arg in script_args:
        p_args.append(arg)
    subprocesses.append(subprocess.Popen(p_args))

def cleanup():
    for p in subprocesses:
        p.terminate()

@pytest.fixture(scope='class')
def webserver_spinup():
    print("Web server spinup...")
    try:
        start_service("../web_server/driver_webserver.py")
        while True:
            try:
                pass
            except KeyboardInterrupt:
                cleanup()
    except Exception as e:
        print(e)
        cleanup()


class WebServer_test:

    # 'routes.main_page' testing ------------------------------------------------------------------------------------
    def test_main_page_response_200_OK(self):
        server_response = requests.get((base_url + "/"))
        assert server_response.status_code == 200

    # 'routes.displaySummary' testing -------------------------------------------------------------------------------
    def test_displaySummary_response_200_OK(self):
        next_command = {"Command": "DISPLAY_SUMMARY", "userid": "j_doe"}
        server_response = requests.post((base_url + CommandURLs.DISPLAY_SUMMARY.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.addFunds' testing -------------------------------------------------------------------------------------
    def test_addFunds_response_200_OK(self):
        next_command = {"Command": "ADD", "userid": "j_doe", "amount": "5000.00"}
        server_response = requests.post((base_url + CommandURLs.ADD.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.getQuote' testing -------------------------------------------------------------------------------------
    def test_getQuote_response_200_OK(self):
        next_command = {"Command": "QUOTE", "userid": "j_doe", "StockSymbol": "ABC"}
        server_response = requests.post((base_url + CommandURLs.QUOTE.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.buyStock' testing -------------------------------------------------------------------------------------
    def test_buyStock_response_200_OK(self):
        next_command = {"Command": "BUY", "userid": "j_doe", "StockSymbol": "ABC", "amount": "200.00"}
        server_response = requests.post((base_url + CommandURLs.BUY.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.commitBuy' testing ------------------------------------------------------------------------------------
    def test_commitBuy_response_200_OK(self):
        next_command = {"Command": "COMMIT_BUY", "userid": "j_doe"}
        server_response = requests.post((base_url + CommandURLs.COMMIT_BUY.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.cancelBuy' testing ------------------------------------------------------------------------------------
    def test_cancelBuy_response_200_OK(self):
        next_command = {"Command": "CANCEL_BUY", "userid": "j_doe"}
        server_response = requests.post((base_url + CommandURLs.CANCEL_BUY.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.sellStock' testing ------------------------------------------------------------------------------------
    def test_sellStock_response_200_OK(self):
        next_command = {"Command": "SELL", "userid": "j_doe", "StockSymbol": "ABC", "amount": "5"}
        server_response = requests.post((base_url + CommandURLs.SELL.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.commitSell' testing -----------------------------------------------------------------------------------
    def test_commitSell_response_200_OK(self):
        next_command = {"Command": "COMMIT_SELL", "userid": "j_doe"}
        server_response = requests.post((base_url + CommandURLs.COMMIT_SELL.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.cancelSell' testing -----------------------------------------------------------------------------------
    def test_cancelSell_response_200_OK(self):
        next_command = {"Command": "CANCEL_SELL", "userid": "j_doe"}
        server_response = requests.post((base_url + CommandURLs.CANCEL_SELL.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.setBuyAmount' testing ---------------------------------------------------------------------------------
    def test_setBuyAmount_response_200_OK(self):
        next_command = {"Command": "SET_BUY_AMOUNT", "userid": "j_doe", "StockSymbol": "CBA", "amount": "150.00"}
        server_response = requests.post((base_url + CommandURLs.SET_BUY_AMOUNT.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.cancelSetBuy' testing ---------------------------------------------------------------------------------
    def test_cancelSetBuy_response_200_OK(self):
        next_command = {"Command": "CANCEL_SET_BUY", "userid": "j_doe", "StockSymbol": "CBA"}
        server_response = requests.post((base_url + CommandURLs.CANCEL_SET_BUY.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.setBuyTrigger' testing --------------------------------------------------------------------------------
    def test_setBuyTrigger_response_200_OK(self):
        next_command = {"Command": "SET_BUY_TRIGGER", "userid": "j_doe", "StockSymbol": "CAB", "amount": "15.00"}
        server_response = requests.post((base_url + CommandURLs.SET_BUY_TRIGGER.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.setSellAmount' testing --------------------------------------------------------------------------------
    def test_setSellAmount_response_200_OK(self):
        next_command = {"Command": "SET_SELL_AMOUNT", "userid": "j_doe", "StockSymbol": "ABC", "amount": "5"}
        server_response = requests.post((base_url + CommandURLs.SET_SELL_AMOUNT.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.cancelSetSell' testing --------------------------------------------------------------------------------
    def test_cancelSetSell_response_200_OK(self):
        next_command = {"Command": "CANCEL_SET_SELL", "userid": "j_doe", "StockSymbol": "ABC"}
        server_response = requests.post((base_url + CommandURLs.CANCEL_SET_SELL.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.setSellTrigger' testing -------------------------------------------------------------------------------
    def test_setSellTrigger_response_200_OK(self):
        next_command = {"Command": "SET_SELL_TRIGGER", "userid": "j_doe", "StockSymbol": "ABC", "amount": "150.00"}
        server_response = requests.post((base_url + CommandURLs.SET_SELL_TRIGGER.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.dumpLog[user]' testing --------------------------------------------------------------------------------
    def test_dumpLog_response_200_OK(self):
        next_command = {"Command": "DUMPLOG", "userid": "j_doe", "filename": "user_dumplog_test.txt"}
        server_response = requests.post((base_url + CommandURLs.DUMPLOG.value), data=next_command)
        assert server_response.status_code == 200

    # 'routes.dumpLog[admin]' testing -------------------------------------------------------------------------------
    def test_dumpLog_response_200_OK(self):
        next_command = {"Command": "DUMPLOG", "filename": "admin_dumplog_test.txt"}
        server_response = requests.post((base_url + CommandURLs.DUMPLOG.value), data=next_command)
        assert server_response.status_code == 200
    # ----------------------------------