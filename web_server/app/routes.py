from flask import render_template, request, jsonify
from app import app
import json
import socket
import sys

# Create the socket for transaction server communication
sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sckt_trans.settimeout(4)
# Create the socket for audit server communication
sckt_audit = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# transaction_server_ip = "192.168.1.178"  # IP on comp 05
transaction_server_ip = "localhost"  # IP on home comp
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
sckt_trans.connect((transaction_server_ip, 44415))


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

