from flask import render_template, request
from app import app
import json


@app.route('/')
def main_page():
    return render_template('day_trader.html')


@app.route('/addFunds', methods=["POST"])
def addFunds():
    form_dict = request.form
    amount = form_dict["amount"]
    # TODO: use 'amount' variable in further processing

    return {"code": "200"}


@app.route('/buyStock', methods=["POST"])
def buyStock():
    form_dict = request.form
    symbol = form_dict["symbol"]
    amount = form_dict["amount"]
    # TODO: use 'amount' variable in further processing

    return {"code": "200"}


@app.route('/sellStock', methods=["POST"])
def sellStock():
    form_dict = request.form
    symbol = form_dict["symbol"]
    amount = form_dict["amount"]
    # TODO: use 'amount' variable in further processing

    return {"code": "200"}


@app.route('/getQuote', methods=["POST"])
def getQuote():
    form_dict = request.form
    symbol = form_dict["symbol"]
    # TODO: use 'amount' variable in further processing

    return {"code": "200"}


@app.route('/buyTrigger', methods=["POST"])
def buyTrigger():
    form_dict = request.form
    symbol = form_dict["symbol"]
    price = form_dict["price"]
    # TODO: use 'amount' variable in further processing

    return {"code": "200"}


@app.route('/sellTrigger', methods=["POST"])
def sellTrigger():
    form_dict = request.form
    symbol = form_dict["symbol"]
    price = form_dict["price"]
    # TODO: use 'amount' variable in further processing

    return {"code": "200"}


@app.route('/getLogFile', methods=["POST"])
def getLogFile():
    # return render_template('log_download.html')

    return {"code": "200"}