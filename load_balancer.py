import socket
import json
import asyncio
import queue
import threading
BUFFER_SIZE = 4096

# list of {ip_address, port, socket} dicts for each web server
servers = []

# dict of user/socket key/value pairs
users = {}

load_balancer_host = "0.0.0.0"
load_balancer_port = 44420
next_server_index = 0
request_q_mutex = threading.Lock()
response_q_mutex = threading.Lock()

def initialize():
    for server in servers:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server["socket"] = s
        s.connect((server["ip_address"], server["port"]))

def terminate_sockets():
    for server in servers:
        s = server["socket"]
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        del server["socket"]

def users_distribution():
    user_ids = users.keys()
    distribution = {}
    for user_id in user_ids:
        server = servers[user_ids[user_id]]
        distribution[user_id] = {"ip_address": server["ip_address"], "port": server["port"]}
    return json.dumps(distribution)

def next_avialable_server():
    # round robin
    next_server_index = (next_server_index + 1) % len(servers)
    return servers[next_server_index]

# returns a Future that holds the response data, when it is fulfilled
async def send(data, username, response_queue):
    _socket = users[username]["socket"]
    def _send(_future, _socket, data):
        _future.set_future(
            _socket.sendall(data)
        )
    loop = asyncio.get_running_loop()
    _future = loop.create_future()
    loop.create_task(_send(_future, _socket, data))
    response = await _future
    response_q_mutex.acquire()
    try:
        response_queue.put(response)
    finally:
        response_q_mutex.release()

def set_user_relay(username):
    server = next_avialable_server()
    users[username] = {
        "socket": server["socket"]
    }
    print(f"{username} assigned to server:")
    print(f"{server}")

async def receive_requests(main_socket, message_queue):
    while (True):
        try:
            incoming_request = main_socket.recv(BUFFER_SIZE).decode()
            print("load balancer has received an incoming request:")
            print(incoming_request)
            request_q_mutex.acquire()
            message_queue.put(incoming_request)
        except Exception as e:
            print("Exception in load balancer:")
            print(e)
            main_socket.shutdown(socket.SHUT_RDWR)
            main_socket.close()
        finally:
            request_q_mutex.release()

async def poll_response_queue(response_queue, main_socket):
    while (True):
        try:
            if (response_queue.qsize() > 0):
                request_q_mutex.acquire()
                if (response_queue.qsize() > 0): # check again if the queue is nonempty, otherwise there's a chance for get() to block and cause a deadlock if send() needs the mutex
                    response = response_queue.get() # will block if the queue is empty
                    main_socket.sendall(response)
        except Exception as e:
            print(e)
        finally:
            request_q_mutex.release()

async def relay(data, response_queue):
    try:
        username = data["userid"]
        try:
            users[username]
        except KeyError:
            set_user_relay(username)
        send(data, username, response_queue)
    except KeyError:
        print(f"no userid field in request payload: {data}")
    except Exception as e:
        print("EXCEPTION OCCURRED:")
        print(e)

def poll_message_queue(message_queue):
    while (True):
        try:
            if (message_queue.qsize() > 0):
                request_q_mutex.acquire()
                if (message_queue.qsize() > 0): # check again if the queue is nonempty, otherwise there's a chance for get() to block and cause a deadlock if receive_requests() needs the mutex
                    message = message_queue.get() # will block if the queue is empty
                    asyncio.run(relay(message))
        finally:
            request_q_mutex.release()

if __name__ == "__main__":
    try:
        message_queue = queue.SimpleQueue()
        response_queue = queue.SimpleQueue()
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_socket.bind((load_balancer_host, load_balancer_port))
        main_socket.listen(10)
        print(f"load balancer service running on {load_balancer_host}:{load_balancer_port}...")
        asyncio.run(poll_response_queue(response_queue, main_socket))
        asyncio.run(receive_requests(main_socket, message_queue, response_queue))
        # invokes infinite synchronous loop:
        poll_message_queue(message_queue)
    except KeyboardInterrupt:
        terminate_sockets()
        main_socket.shutdown(socket.SHUT_RDWR)
        main_socket.close()