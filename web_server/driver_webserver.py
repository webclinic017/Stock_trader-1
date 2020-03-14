import socket
import json
import os
import multiprocessing

BUFFER_SIZE = 4096
protocol = "http"
server_name = "web server"

# transaction_server_ip = "192.168.1.229"  # IP on comp 17
transaction_server_ip = os.environ['TRANS_HOST']
audit_log_server_ip = os.environ['LOG_HOST']  # IP on home comp
transaction_server_port = os.environ['TRANS_PORT']
audit_log_server_port = os.environ['LOG_HOST']
# static_server_host = os.environ['MY_HOST']
# static_server_port = os.environ['MY_HOST']
web_server_host = os.environ['MY_HOST']
web_server_port = os.environ['MY_PORT']
base_url = f"{web_server_host}:{web_server_port}"

print(str(os.environ['MY_HOST']))
print(web_server_port)


def send_to_trans_server(transaction_payload):
    sckt_trans = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt_trans.connect((transaction_server_ip, transaction_server_port))

    # Forward request
    sckt_trans.sendall(str.encode(json.dumps(transaction_payload)))

    # Receive response
    trans_response = sckt_trans.recv(BUFFER_SIZE).decode()
    print("--RESPONSE:" + str(trans_response))
    sckt_trans.close()

    return str.encode(trans_response)


def is_index_route(http_request):
    first_line = http_request.split("\n")[0]
    endpoint = first_line.split(" ")[1]
    result = endpoint == "/"
    return result


def get_transaction_payload(http_request):
    return http_request.split("\n")[-1]


def listen():
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.bind((web_server_host, int(web_server_port)))
    print("listening on " + str(web_server_host) + ":" + str(web_server_port))
    web_socket.listen(10)
    while (True):
        try:
            conn, addr = web_socket.accept()
            print("awaiting incoming request...")
            incoming_request = conn.recv(BUFFER_SIZE).decode()
            print(incoming_request)
            if (len(incoming_request) > 0):
                print("incoming request:")
                print(incoming_request)
                if (not is_index_route(incoming_request)):
                    transaction_payload = get_transaction_payload(incoming_request)
                    response = send_to_trans_server(transaction_payload)
                else:
                    response = main_page()
                conn.sendto(response, addr)
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
        except OSError as e:
            print("OSError raised in web server")
        except Exception as e:
            print("Exception in web server")
            print(type(e))
            print(e)


def main_page():
    print("index route invoked")
    return str.encode("landing page stub")
    # return render_template("day_trader.html")


if __name__ == "__main__":
    listen()
