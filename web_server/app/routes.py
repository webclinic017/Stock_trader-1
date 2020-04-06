from flask import render_template, request, jsonify
import requests
from app import app
import json
import socket
import sys


@app.route('/')
def main_page():
    return render_template('login_form.html')


@app.route('/day_trader')
def day_trader():
    return render_template('day_trader.html')
