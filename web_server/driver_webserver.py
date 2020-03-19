import socket
import json
import threading
import requests
import os
from dotenv import load_dotenv
load_dotenv()
BUFFER_SIZE = 4096
protocol = "http"
server_name = "web server"

# transaction_server_ip = "192.168.1.229"  # IP on comp 17
transaction_server_ip = os.environ.get("trans_host")
transaction_server_port = os.environ.get("trans_port")
audit_log_server_ip = os.environ.get("audit_log_host")
audit_log_server_port = os.environ.get("audit_log_port")
web_server_host = os.environ.get("web_host")
web_server_port = os.environ.get("web_port")
base_url = f"{web_server_host}:{web_server_port}"

def send_to_trans_server(transaction_payload):

    sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt_trans.connect((transaction_server_ip, int(transaction_server_port)))

    # Forward request
    sckt_trans.sendall(str.encode(json.dumps(transaction_payload)))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    sckt_trans.close()

    return trans_response

def get_route(http_request):
    first_line = http_request.split("\n")[0]
    route = first_line.split(" ")[1]
    return route

def dumpLog(data):
    response = requests.post(f"{protocol}://{audit_log_server_ip}:{audit_log_server_port}/dumpLog", json=data).json()
    return json.dumps(response)

def get_data(http_request):
    return http_request.split("\n")[-1]

class ConnectionThread(threading.Thread):
    def __init__(self, workload_conn, addr):
        super().__init__()
        self.workload_conn = workload_conn
        self.addr = addr
    def run(self):
        conn = self.workload_conn
        incoming_request = conn.recv(BUFFER_SIZE).decode()
        if (len(incoming_request) > 0):
            route = get_route(incoming_request)
            if (route == "/dumpLog"):
                response = dumpLog(get_data(incoming_request))
            elif (route == "/"):
                response = main_page()
            else:
                transaction_payload = get_data(incoming_request)
                response = send_to_trans_server(transaction_payload)
            conn.sendto(str.encode(response), self.addr)
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except OSError as e:
            print(f"\033[1;31mWeb_Srv:{e}\033[0;0m")

def listen():
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.bind((web_server_host, int(web_server_port)))
    web_socket.listen(1500)
    while (True):
        try:
            workload_conn, addr = web_socket.accept()
            connection_thread = ConnectionThread(workload_conn=workload_conn, addr=addr)
            connection_thread.start()
        except Exception as e:
            print(f"\033[1;31mWeb_Srv:{type(e)}\033[0;0m")
            print(f"\033[1;31m{e}\033[0;0m")

def main_page():
    return "landing page stub"
    #return render_template("day_trader.html")

if __name__ == "__main__":
    listen()