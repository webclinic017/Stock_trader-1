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
lb_socks = 0
ts_socks = 0

# transaction_server_ip = "192.168.1.229"  # IP on comp 17
transaction_server_ip = os.environ.get("trans_host")
transaction_server_port = int(os.environ.get("trans_port"))
audit_log_server_ip = os.environ.get("audit_log_host")
audit_log_server_port = int(os.environ.get("audit_log_port"))
web_server_host = os.environ.get("web_host")
web_server_port = int(os.environ.get("web_port"))
base_url = f"{web_server_host}:{web_server_port}"

def send_to_trans_server(transaction_payload):
    global ts_socks
    sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt_trans.connect((transaction_server_ip, transaction_server_port))
    ts_socks += 1

    # Forward request
    sckt_trans.sendall(str.encode(json.dumps(transaction_payload)))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    sckt_trans.close()
    ts_socks -= 1
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
        global lb_socks
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
            # conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            print("WS->LB SCKT closed")
            lb_socks -= 1
        except OSError as e:
            print(f"\033[1;31mWeb_Srv.run:{e}\033[0;0m")

class ConnectionPool:
    def __init__(self):
        self.pool = []
    def add_connection(self, connection_thread):
        connection_thread.start()
        self.pool.append(connection_thread)
    def number_of_active_connections(self):
        num = 0
        for conn in self.pool:
            if (conn.is_alive()):
                num = num + 1
        return num
    def __repr__(self):
        string = "---------------\nconnection pool: \n"
        for conn in self.pool:
            string = string + "\n" + str(conn.is_alive())
        return string + "\n---------------\n"

def listen():
    global lb_socks
    global ts_socks
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.bind((web_server_host, web_server_port))
    web_socket.listen(1500)
    connection_pool = ConnectionPool()
    while (True):
        try:
            workload_conn, addr = web_socket.accept()
            lb_socks += 1
            connection_thread = ConnectionThread(workload_conn=workload_conn, addr=addr)
            connection_pool.add_connection(connection_thread)
            print(f"number of active connections: {connection_pool.number_of_active_connections()}")
        except Exception as e:
            print(f"\033[1;31mWeb_Srv.listen:{type(e)}\033[0;0m")
            print(f"\033[1;31mWeb_Srv.listen{e}\033[0;0m")
        print(f"\033[1;35mWEB_SRV-ld_bln_socks:{lb_socks} | trans_socks:{ts_socks} | threads:{threading.active_count()}\033[0;0m")

def main_page():
    return "landing page stub"
    #return render_template("day_trader.html")

if __name__ == "__main__":
    listen()