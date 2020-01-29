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


@app.route('/')
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


@app.route('/buyTrigger', methods=["POST"])
def buyTrigger():
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


@app.route('/sellTrigger', methods=["POST"])
def sellTrigger():
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


@app.route('/getLogFile', methods=["POST"])
def getLogFile():
    # request_dict = json.dumps(request.form.to_dict(flat=True))
    # print("--REQUEST:" + request_dict)
    # sckt_audit.sendall(str.encode(request_dict))

    # return render_template('log_download.html')

    # Receive response - logfile
    # TODO: Parse the large log file to be returned
    # response = sckt_audit.recv(65536).decode()
    # print("--RESPONSE:" + str(response))

    # TODO: start the logfile.txt download for user

    return "OK", 200

# addFundJSON = {
#         "Command": "BUY",
#         "userid": "jdoe",
#         "StockSymbol": "ABC",
#         "amount": 256.00
#     }
