import socket
import json
import multiprocessing
import requests
import os
BUFFER_SIZE = 4096
protocol = "http"
server_name = "web server"

# transaction_server_ip = "192.168.1.229"  # IP on comp 17
transaction_server_ip = os.environ.get('TRANS_HOST', default="localhost")
transaction_server_port = os.environ.get('TRANS_PORT', default=44415)
audit_log_server_ip = os.environ.get("LOG_HOST", default="localhost")
audit_log_server_port = os.environ.get("LOG_PORT", default=44416)
web_server_host = os.environ.get("WEB_HOST", default="localhost")
web_server_port = os.environ.get("WEB_PORT", default=44419)
base_url = f"{web_server_host}:{web_server_port}"

def send_to_trans_server(transaction_payload):

    sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt_trans.connect((transaction_server_ip, transaction_server_port))

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

def listen():
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.bind((web_server_host, web_server_port))
    web_socket.listen(10)
    while (True):
        try:
            conn, addr = web_socket.accept()
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
                conn.sendto(str.encode(response), addr)
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
        except OSError as e:
            print("OSError raised in web server")
        except Exception as e:
            print("Exception in web server")
            print(type(e))
            print(e)

def main_page():
    return "landing page stub"
    #return render_template("day_trader.html")

if __name__ == "__main__":
    listen()