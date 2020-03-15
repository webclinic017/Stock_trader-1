import socket
import json
import threading
import queue
import random
BUFFER_SIZE = 4096
load_balancer_host = "localhost"
load_balancer_port = 44420
next_server_index = [0]

class Server:
    def __init__(self, ip_addr, port):
        self.ip_addr = ip_addr
        self.port = port
        self.socket = None
    def connect_socket(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect((self.ip_addr, self.port))
        self.socket = _socket
    def send(self, data):
        if (self.socket):
            self.socket.sendall(str.encode(data))
    def recv(self):
        response = self.recvall().decode()
        # if (response == ""):
        #     self.close_socket()
        #     return None
        # else:
        return response
    def close_socket(self):
        try:
            if (self.socket):
                _socket = self.socket
                _socket.shutdown(socket.SHUT_RDWR)
                _socket.close()
        except OSError:
            pass

    def recvall(self):
        # Helper function to recv all bytes from response
        # Must have server side close connection when finished to ensure EOF is caught on this end.
        data = bytearray()
        while True:
            packet = self.socket.recv(BUFFER_SIZE)
            if not packet:
                self.close_socket()
                break
            data.extend(packet)
        return data

    def __str__(self):
        return f"{self.ip_addr}:{self.port}"
    def __repr__(self):
        return self.__str__()

# list of {ip_address, port, socket} dicts for each web server
servers = [
    Server("localhost", 44419)
]

# dict of user/socket key/value pairs
users = {}

class ConnectionThread(threading.Thread):
    def __init__(self, server, workload_conn, message):
        super().__init__()
        self.server = server
        self.workload_conn = workload_conn
        self.message = message

    def run(self):
        print("----")
        print(f"connecting to {server}")
        self.server.connect_socket()
        print(f"sending:")
        print(self.message)
        self.server.send(self.message)
        print("sent! waiting on response...")
        response = self.server.recv()
        if (response != None and len(response) > 0):
            print(f"received response")
            # print(response)
            print("sending back to client...")
            self.workload_conn.send(str.encode(response))
            print("sent!")
        else:
            print("no response, closing socket....")
            self.server.close_socket()
            print("socket closed")
        print("----")

def terminate_sockets():
    [server.close_socket() for server in servers]

def users_distribution_report():
    user_ids = users.keys()
    distribution = {}
    for user_id in user_ids:
        server = users[user_id]
        distribution[user_id] = str(server)
    return json.dumps(distribution)

def assign_next_available_server():
    # round robin
    next_server_index[0] = (next_server_index[0] + 1) % len(servers)
    return servers[next_server_index[0]]

def assign_random_server():
    return servers[random.randint(0, len(servers) - 1)]

def set_user_relay(username):
    if (username == None):
        server = assign_random_server()
    else:
        try:
            server = users[username]
        except KeyError:
            server = assign_next_available_server()
            users[username] = server
            print(f"{username} assigned to server: {str(server)}")
    return server

def get_username_from_query_string(self, query_str):
    args = query_str.split("&")
    username_arg = [arg for arg in args if query_str in arg]
    if (len(username_arg) == 0):
        username = None
    else:
        username = username_arg[0].split("=")[-1]
    return username

def get_username_from_json(json_str):
    try:
        username = json.loads(json_str)["userid"]
    except KeyError:
        username = None
    return username

def get_username(message):
    message_lines = message.split("\n")
    query = message_lines[-1]
    username = get_username_from_json(query)
    return username

if __name__ == "__main__":
    try:
        workload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        workload_socket.bind((load_balancer_host, load_balancer_port))
        workload_socket.listen(1500)
        print(f"load balancer service running on {load_balancer_host}:{load_balancer_port}...")
        while (True):
            workload_conn, addr = workload_socket.accept()
            incoming_message = workload_conn.recv(BUFFER_SIZE).decode()
            if (len(incoming_message) > 0):
                username = get_username(incoming_message)
                server = set_user_relay(username)
                connection_thread = ConnectionThread(server, workload_conn, incoming_message)
                connection_thread.start()
    except Exception as e:
        print(type(e))
        print(e)
    finally:
        print("\n" +"distribution report:")
        print(users_distribution_report())
        terminate_sockets()
