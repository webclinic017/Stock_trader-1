from flask import render_template, request, jsonify
import requests
from app import app
import json
import socket
import sys
from AuditLogBuilder import AuditLogBuilder

# Create the socket for transaction server communication
sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Create the socket for audit server communication
sckt_audit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

protocol = "http"
server_name = "server_name_placeholder"

# transaction_server_ip = "192.168.1.178"  # IP on comp 05
transaction_server_ip = audit_log_server_ip = "localhost"  # IP on home comp
transaction_server_port = 44415
audit_log_server_port = 44416

port_range = (44415, 44420)  # (inclusive,exclusive)


def find_open_socket(addr, ports):
    for i in range(ports[0], ports[1]):
        try:
            sckt_trans.connect((addr, i))
            print("connected on port:" + str(i))
            return
        except Exception as e:
            print(str(i), end="")
            print(e)
            continue


# Create connection an any available ports
# find_open_socket(transaction_server_ip, port_range)
sckt_trans.connect((transaction_server_ip, transaction_server_port))
sckt_audit.connect((audit_log_server_ip, audit_log_server_port))

@app.route("/")
def main_page():
    return render_template("day_trader.html")

@app.route("/testconn", methods=["GET"])
def testconn():
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    return {"hello": "12", "bye": "13"}


@app.route('/addFunds', methods=["POST"])
def addFunds():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    audit_log_json = AuditLogBuilder("ADD", server_name).build(request_dict)
    requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/auditLog", audit_log_json)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(1024).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(1024).decode()
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
    trans_response = sckt_trans.recv(1024).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(1024).decode()
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
    trans_response = sckt_trans.recv(1024).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(1024).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/commitBuy', methods=["POST"])
def commitBuy():
    # TODO:implement commitBuy
    return "OK", "200"


@app.route('/cancelBuy', methods=["POST"])
def cancelBuy():
    # TODO:implement cancelBuy
    return "OK", "200"


@app.route('/sellStock', methods=["POST"])
def sellStock():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(1024).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(1024).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/commitSell', methods=["POST"])
def commitSell():
    # TODO:implement commitSell
    return "OK", "200"


@app.route('/cancelSell', methods=["POST"])
def cancelSell():
    # TODO:implement cancelSell
    return "OK", "200"


@app.route('/setBuyAmount', methods=["POST"])
def setBuyAmount():
    # TODO:implement setBuyAmount
    return "OK", "200"


@app.route('/cancelSetBuy', methods=["POST"])
def cancelSetBuy():
    # TODO:implement cancelSetBuy
    return "OK", "200"


@app.route('/setBuyTrigger', methods=["POST"])
def setBuyTrigger():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(1024).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(1024).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/setSellAmount', methods=["POST"])
def setSellAmount():
    # TODO:implement setSellAmount
    return "OK", "200"


@app.route('/cancelSetSell', methods=["POST"])
def cancelSetSell():
    # TODO:implement cancelSetSell
    return "OK", "200"


@app.route('/setSellTrigger', methods=["POST"])
def setSellTrigger():
    # Send request
    request_dict = json.dumps(request.form.to_dict(flat=True))
    print("--REQUEST:" + request_dict)
    sckt_trans.sendall(str.encode(request_dict))

    # TODO: send client REQUEST LOG to the audit server
    # sckt_audit.sendall(str.encode(request_dict))

    # Receive response
    trans_response = sckt_trans.recv(1024).decode()
    print("--RESPONSE:" + str(trans_response))

    # TODO: send transaction server RESPONSE LOG to the audit server
    # sckt_audit.sendall(str.encode(response))
    # audit_response = sckt_audit.recv(1024).decode()
    # print("RESPONSE:" + str(audit_response))

    return trans_response


@app.route('/dumpLog', methods=["GET"])
def dumpLog():
    response = requests.get(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/dumpLog").json()
    return json.dumps(response)

    # request_dict = json.dumps(request.form.to_dict(flat=True))
    # print("--REQUEST:" + request_dict)
    # sckt_audit.sendall(str.encode(request_dict))
    # TODO: determine if it is user or admin dump
    # return render_template('log_download.html')

    # Receive response - logfile
    # TODO: Parse the large log file to be returned
    # response = sckt_audit.recv(65536).decode()
    # print("--RESPONSE:" + str(response))

    # TODO: start the logfile.txt download for user

    return "OK", 200

@app.route('/displaySummary', methods=["POST"])
def displaySummary():
    # TODO:implement displaySummary
    return "OK", "200"
