import socket
import json
import threading
import queue
import threading

BUFFER_SIZE = 4096
load_balancer_host = "localhost"
load_balancer_port = 44421
next_server_index = [0]
request_q_mutex = threading.Lock()
response_q_mutex = threading.Lock()

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
        if (self.socket):
            return self.socket.recv(BUFFER_SIZE).decode()
        return ""
    def close_socket(self):
        if (self.socket):
            _socket = self.socket
            _socket.shutdown(socket.SHUT_RDWR)
            _socket.close()
            del self.socket
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

class ResponsePoller(threading.Thread):
    def __init__(self, response_queue, conn):
        super().__init__()
        self.response_queue = response_queue
        self.conn = conn
    def run(self):
        response_queue = self.response_queue
        conn = self.conn
        while (True):
            try:
                if (response_queue.qsize() > 0):
                    print("ResponsePoller: waiting to acquire response queue mutex")
                    response_q_mutex.acquire()
                    print("ResponsePoller: acquired response queue mutex")
                    try:
                        if (response_queue.qsize() > 0): # check again if the queue is nonempty, otherwise there's a chance for get() to block and cause a deadlock if send() needs the mutex
                            response = response_queue.get() # will block if the queue is empty
                            print("response:")
                            print(response)
                            conn.sendall(str.encode(response))
                    finally:
                        response_q_mutex.release()
                        print("ResponsePoller: response queue mutex released")
            except Exception as e:
                print("Exception raised in ResponsePoller")
                print(e)
                break

class RequestPoller(threading.Thread):
    def __init__(self, conn, request_queue):
        super().__init__()
        self.conn = conn
        self.request_queue = request_queue
    def run(self):
        conn = self.conn
        request_queue = self.request_queue
        while (True):
            try:
                incoming_request = conn.recv(BUFFER_SIZE).decode()
                if (len(incoming_request) > 0):
                    print("load balancer has received an incoming request:")
                    print(incoming_request)
                    request_q_mutex.acquire()
                    try:
                        request_queue.put(incoming_request)
                    finally:
                        request_q_mutex.release()
            except Exception as e:
                print("Exception raised in RequestPoller")
                print(e)
                break

def initialize():
    [server.connect_socket() for server in servers]

def terminate_sockets():
    [server.close_socket() for server in servers]

def users_distribution_report():
    user_ids = users.keys()
    distribution = {}
    for user_id in user_ids:
        server = users[user_id]
        distribution[user_id] = str(server)
    return json.dumps(distribution)

def next_available_server():
    # round robin
    next_server_index[0] = (next_server_index[0] + 1) % len(servers)
    return servers[next_server_index[0]]

# returns a Future that holds the response data, when it is fulfilled
def send(data, username, response_queue):
    server = users[username]
    print(f"send data to {str(server)}")
    server.send(data)
    print("...sent")
    response = ""
    while (response == ""):
        response = server.recv()
    print(f"received response from {str(server)}: {response}")
    print("send(): waiting to acquire response queue mutex")
    response_q_mutex.acquire()
    print("send(): response queue mutex aquired")
    try:
        response_queue.put(response)
    finally:
        response_q_mutex.release()
        print("send(): response queue mutex released")

def set_user_relay(username):
    server = next_available_server()
    users[username] = server
    print(f"{username} assigned to server: {str(server)}")

def get_username_from_query_string(self, query_str):
    args = query_str.split("&")
    username_arg = [arg for arg in args if query_str in arg]
    if (len(username_arg) == 0):
        username = None
    else:
        username = username_arg[0].split("=")[-1]

def get_username_from_json(json_str):
    try:
        print("trace1")
        username = json.loads(json_str)["userid"]
        print("trace2")
    except KeyError:
        username = None
    return username

def get_username(message):
    message_lines = message.split("\n")
    query = message_lines[-1]
    username = get_username_from_json(query)
    return username

def relay(message, response_queue):
    try:
        username = get_username(message)
        if (username == None):
            raise Exception(f"no userid field in request payload: {message}")
        set_user_relay(username)
        send(message, username, response_queue)
    except Exception as e:
        print("EXCEPTION OCCURRED:")
        print(e)

def relay_incoming_messages(conn, request_queue, response_queue):
    while (True):
        if (request_queue.qsize() > 0):
            request_q_mutex.acquire()
            try:
                if (request_queue.qsize() > 0): # check again if the queue is nonempty, otherwise there's a chance for get() to block and cause a deadlock if receive_requests() needs the mutex
                    message = request_queue.get() # will block if the queue is empty
                    relay(message, response_queue)
            finally:
                request_q_mutex.release()

if __name__ == "__main__":
    try:
        initialize()
        request_queue = queue.Queue()
        response_queue = queue.Queue()
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_socket.bind((load_balancer_host, load_balancer_port))
        main_socket.listen(10)
        print(f"load balancer service running on {load_balancer_host}:{load_balancer_port}...")
        workload_sckt, addr = main_socket.accept()

        print(f"connection established with {addr}")
        response_queue_poller = ResponsePoller(response_queue, workload_sckt)
        response_queue_poller.start()
        # invokes infinite synchronous loop:
        request_queue_poller = RequestPoller(workload_sckt, request_queue)
        request_queue_poller.start()
        relay_incoming_messages(workload_sckt, request_queue, response_queue)
    except Exception as e:
        print("Exception in load balancer:")
        print(e)
    finally:
        print("\n" +"distribution report:")
        print(users_distribution_report())
        terminate_sockets()
        if (workload_sckt):
            main_socket.shutdown(socket.SHUT_RDWR)
            main_socket.close()
        response_queue_poller.join()
        request_queue_poller.join()