from flask import render_template, request, jsonify
from app import app
import json
import socket
import sys

# Create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create connection
s.connect("", "44415")


@app.route('/')
def main_page():
    return render_template("day_trader.html")


@app.route('/addFunds', methods=["POST"])
def addFunds():
    form_dict = request.form

    # TODO: send request to the audit server

    # TODO: send request to the transaction server
    # addFundJSON = {
    #     "Command": "ADD",
    #     "userid": "jdoe",
    #     "StockSymbol": "ABC",
    #     "amount": 256.00
    # }

    return {"code": "200"}


@app.route('/buyStock', methods=["POST"])
def buyStock():
    form_dict = request.form
    # TODO: send request to the audit server

    # TODO: send request to the transaction server

    return {"code": "200"}


@app.route('/sellStock', methods=["POST"])
def sellStock():
    form_dict = request.form
    # TODO: send request to the audit server

    # TODO: send request to the transaction server

    return {"code": "200"}


@app.route('/getQuote', methods=["POST"])
def getQuote():
    form_dict = request.form
    # TODO: send request to the audit server

    # TODO: send request to the transaction server

    return {"code": "200"}


@app.route('/buyTrigger', methods=["POST"])
def buyTrigger():
    form_dict = request.form
    # TODO: send request to the audit server

    # TODO: send request to the transaction server

    return {"code": "200"}


@app.route('/sellTrigger', methods=["POST"])
def sellTrigger():
    form_dict = request.form
    # TODO: send request to the audit server

    # TODO: send request to the transaction server

    return {"code": "200"}


@app.route('/getLogFile', methods=["POST"])
def getLogFile():
    # return render_template('log_download.html')
    # TODO: send request to the audit server

    # TODO: send request to the transaction server
    return {"code": "200"}

# addFundJSON = {
#         "Command": "BUY",
#         "userid": "jdoe",
#         "StockSymbol": "ABC",
#         "amount": 256.00
#     }