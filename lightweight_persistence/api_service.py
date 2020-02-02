from flask import Flask, app, request
from logger import logger
import json.tool
app = Flask(__name__)

audit_log_server_ip = "localhost"
audit_log_server_port = 44416

logger_instance = None

@app.route("/getCurrentTransactionNum", methods=["POST"])
def get_current_transaction_num():
    current_transaction_num = logger_instance.get_current_transaction_num()
    return json.dumps({"status": "SUCCESS", "data": current_transaction_num})

@app.route("/getNextTransactionNum", methods=["POST"])
def get_next_transaction_num():
    next_transaction_num = logger_instance.get_next_transaction_num()
    return json.dumps({"status": "SUCCESS", "data": next_transaction_num})

@app.route("/auditLog", methods=["POST"])
def insert_log():
    data = request.json
    response = logger_instance.insert_log(data)
    return json.dumps(response)

@app.route("/dumpLog", methods=["POST"])
def get_logs():
    data = request.json
    response = logger_instance.get_logs(data)
    return json.dumps(response)

@app.route("/debug", methods=["GET"])
def debug():
    audit_log = logger_instance.debug()
    return json.dumps({"status": "SUCCESS", "data": audit_log})

if __name__ == "__main__":
    logger_instance = logger()
    app.run(host=audit_log_server_ip, port=audit_log_server_port)