from flask import Flask, app, request
from logger import logger
import json.tool
app = Flask(__name__)

audit_log_server_ip = "localhost"
audit_log_server_port = 44416

logger_instance = None

@app.route("/auditLog", methods=["POST"])
def insert_log():
    data = request.json
    response = logger_instance.insert_log(data)
    return json.dumps(response)

@app.route("/dumpLog", methods=["GET"])
def get_logs():
    response = logger_instance.get_logs()
    return json.dumps(response)

if __name__ == "__main__":
    logger_instance = logger()
    app.run(host=audit_log_server_ip, port=audit_log_server_port)