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
        response = self.socket.recv(BUFFER_SIZE).decode()
        if (response == ""):
            self.close_socket()
            return None
        else:
            return response
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

class ConnectionThread(threading.Thread):
    def __init__(self, server, workload_conn, message):
        super().__init__()
        self.server = server
        self.workload_conn = workload_conn
        self.message = message
    def run(self):
        print("sending...")
        self.server.connect_socket()
        self.server.send(self.message)
        print("sent")
        print("waiting for response...")
        response = self.server.recv()
        print("received response")
        print("----")
        print(response)
        print("----")
        self.workload_conn.send(str.encode(response))
        print("sent response")

# asynchronous thread that sends responses in the response queue to the write socket (to workload source)
class ResponsePoller(threading.Thread):
    def __init__(self, response_queue, write_socket):
        super().__init__()
        self.response_queue = response_queue
        self.write_socket = write_socket
    def run(self):
        response_queue = self.response_queue
        try:
            if (response_queue.qsize() > 0):
                response_q_mutex.acquire()
                try:
                    if (response_queue.qsize() > 0): # check again if the queue is nonempty, otherwise there's a chance for get() to block and cause a deadlock if send() needs the mutex
                        print(response_queue)
                        response = response_queue.get() # will block if the queue is empty
                        print(response)
                        self.write_socket.sendall(str.encode(response))
                finally:
                    response_q_mutex.release()
        except Exception as e:
            print("Exception raised in ResponsePoller")
            print(type(e))
            print(e)

# asynchronous thread that reads from a connected socket for incoming requests (from workload) and pushes new request to the request queue
class RequestPoller(threading.Thread):
    def __init__(self, request_queue, read_socket):
        super().__init__()
        self.read_socket = read_socket
        self.request_queue = request_queue
    def run(self):
        request_queue = self.request_queue
        read_socket = self.read_socket
        try:
            incoming_request = read_socket.recv(BUFFER_SIZE).decode()
            if (len(incoming_request) > 0):
                print(incoming_request)
                request_q_mutex.acquire()
                try:
                    request_queue.put(incoming_request)
                finally:
                    request_q_mutex.release()
            else:
                try:
                    read_socket.shutdown(socket.SHUT_RDWR)
                    read_socket.close()
                except OSError:
                    pass
        except Exception as e:
            print("Exception raised in RequestPoller")
            print(e)

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
    server.connect_socket()
    server.send(data)
    response_q_mutex.acquire()
    try:
        response = server.recv()
        response_queue.put(response)
    finally:
        response_q_mutex.release()
        server.close_socket()

def set_user_relay(username):
    server = next_available_server()
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

def relay_incoming_messages(request_queue, response_queue):
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
        request_queue = queue.Queue()
        response_queue = queue.Queue()
        workload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        workload_socket.bind((load_balancer_host, load_balancer_port))
        workload_socket.listen(10)
        print(f"load balancer service running on {load_balancer_host}:{load_balancer_port}...")
        while (True):
            workload_conn, addr = workload_socket.accept()
            incoming_message = workload_conn.recv(BUFFER_SIZE).decode()
            if (len(incoming_message) > 0):
                username = get_username(incoming_message)
                server = set_user_relay(username)
                connection_thread = ConnectionThread(server, workload_conn, incoming_message)
                connection_thread.start()
            #response_queue_poller = ResponsePoller(response_queue, workload_conn)
            #response_queue_poller.start()
            #request_queue_poller = RequestPoller(request_queue, workload_conn)
            #request_queue_poller.start()
            #relay_incoming_messages(request_queue, response_queue)
            #response_queue_poller.join()
            #request_queue_poller.join()
            else:
                try:
                    workload_conn.shutdown(socket.SHUT_RDWR)
                    workload_conn.close()
                except OSError as e:
                    print("OSError raised in load balancer")
                    print(e)
    finally:
        print("\n" +"distribution report:")
        print(users_distribution_report())
        terminate_sockets()