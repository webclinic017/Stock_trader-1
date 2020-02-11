from flask import render_template, request, jsonify
import requests
from app import app
import json
import socket
import sys
BUFFER_SIZE = 4096

# Create the socket for transaction server communication
sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Create the socket for audit server communication
sckt_audit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

protocol = "http"
server_name = "web server"

# transaction_server_ip = "192.168.1.178"  # IP on comp 05
transaction_server_ip = audit_log_server_ip = "localhost"  # IP on home comp
transaction_server_port = 44415
audit_log_server_port = 44416

port_range = (44415, 44420)  # (inclusive,exclusive)
transaction_server_stubbed = False
audit_server_stubbed = False

# Create connection an any available ports
# find_open_socket(transaction_server_ip, port_range)
try:
    sckt_trans.connect((transaction_server_ip, transaction_server_port))
except ConnectionRefusedError as e:
    transaction_server_stubbed = True
try:
    sckt_audit.connect((audit_log_server_ip, audit_log_server_port))
except ConnectionRefusedError as e:
    audit_server_stubbed = True

def forward_request_tserver(request_dict):
    if transaction_server_stubbed:
        return str(request_dict)
    else:
        # Forward request
        sckt_trans.sendall(str.encode(request_dict))

        # Receive response
        trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
        print("--RESPONSE:" + str(trans_response))

        # if not audit_server_stubbed:
        #     # TODO: send client REQUEST LOG to the audit server
        #     # sckt_audit.sendall(str.encode(request_dict))
        #
        #     # TODO: send transaction server RESPONSE LOG to the audit server
        #     # sckt_audit.sendall(str.encode(response))
        #     # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
        #     # print("RESPONSE:" + str(audit_response))

        return trans_response

@app.route("/")
def main_page():
    return render_template("day_trader.html")

@app.route('/addFunds', methods=["POST"])
def addFunds():
    # Receive request from client
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

    if transaction_server_stubbed:
        return str(data)
    else:
        response = requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/dumpLog", json=data).json()
        return json.dumps(response)

@app.route('/displaySummary', methods=["POST"])
def displaySummary():
    # Receive request from client
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    return forward_request_tserver(request_dict)
