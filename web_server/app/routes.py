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

# Create connection an any available ports
# find_open_socket(transaction_server_ip, port_range)
sckt_trans.connect((transaction_server_ip, transaction_server_port))
sckt_audit.connect((audit_log_server_ip, audit_log_server_port))

@app.route("/")
def main_page():
    return render_template("day_trader.html")

@app.route('/addFunds', methods=["POST"])
def addFunds():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)

    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/getQuote', methods=["POST"])
def getQuote():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/buyStock', methods=["POST"])
def buyStock():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/commitBuy', methods=["POST"])
def commitBuy():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("COMMIT_BUY", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/cancelBuy', methods=["POST"])
def cancelBuy():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("CANCEL_BUY", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/sellStock', methods=["POST"])
def sellStock():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/commitSell', methods=["POST"])
def commitSell():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("COMMIT_SELL", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/cancelSell', methods=["POST"])
def cancelSell():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("CANCEL_SELL", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/setBuyAmount', methods=["POST"])
def setBuyAmount():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("SET_BUY_AMOUNT", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/cancelSetBuy', methods=["POST"])
def cancelSetBuy():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("CANCEL_SET_BUY", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/setBuyTrigger', methods=["POST"])
def setBuyTrigger():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/setSellAmount', methods=["POST"])
def setSellAmount():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("SET_SELL_AMOUNT", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response

@app.route('/cancelSetSell', methods=["POST"])
def cancelSetSell():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("CANCEL_SET_SELL", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response

@app.route('/setSellTrigger', methods=["POST"])
def setSellTrigger():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))
    return trans_response

@app.route('/dumpLog', methods=["POST"])
def dumpLog():
    data = json.dumps(request.form.to_dict(flat=True))
    response = requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/dumpLog", json=data).json()
    return json.dumps(response)

@app.route('/displaySummary', methods=["POST"])
def displaySummary():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    # audit_log_json = AuditLogBuilder("DISPLAY_SUMMARY", server_name).build(request_dict)
    # requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(BUFFER_SIZE).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response
