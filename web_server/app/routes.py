from flask import render_template, request, jsonify
import requests
from app import app
import json
import socket
import sys
import os

BUFFER_SIZE = 4096

protocol = "http"
server_name = "web server"

# transaction_server_ip = "192.168.1.229"  # IP on comp 17
transaction_server_ip = os.environ['TRANS_HOST']
audit_log_server_ip = os.environ['LOG_HOST'] # IP on home comp
transaction_server_port = os.environ['TRANS_PORT']
audit_log_server_port = os.environ['LOG_PORT']
port_range = (44415, 44420)  # (inclusive,exclusive)

print("transaction server ip = " + str(transaction_server_ip))
print("transaction server port = " + str(transaction_server_port))


def forward_request_tserver(request_dict):

    sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt_trans.connect((transaction_server_ip, transaction_server_port))
    # Forward request

    sckt_trans.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))
    sckt_trans.close()

    return trans_response


@app.route("/")
def main_page():
    return render_template("day_trader.html")


@app.route('/addFunds', methods=["POST"])
def addFunds():
    # Receive request from client
    print("sending to in addFunds method " + str(transaction_server_ip))
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/getQuote', methods=["POST"])
def getQuote():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/buyStock', methods=["POST"])
def buyStock():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/commitBuy', methods=["POST"])
def commitBuy():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/cancelBuy', methods=["POST"])
def cancelBuy():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/sellStock', methods=["POST"])
def sellStock():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/commitSell', methods=["POST"])
def commitSell():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/cancelSell', methods=["POST"])
def cancelSell():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/setBuyAmount', methods=["POST"])
def setBuyAmount():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/cancelSetBuy', methods=["POST"])
def cancelSetBuy():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/setBuyTrigger', methods=["POST"])
def setBuyTrigger():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/setSellAmount', methods=["POST"])
def setSellAmount():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/cancelSetSell', methods=["POST"])
def cancelSetSell():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/setSellTrigger', methods=["POST"])
def setSellTrigger():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)


@app.route('/dumpLog', methods=["POST"])
def dumpLog():
    data = json.dumps(request.form.to_dict(flat=True))
    response = requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/dumpLog", json=data).json()
    return json.dumps(response)


@app.route('/displaySummary', methods=["POST"])
def displaySummary():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)
