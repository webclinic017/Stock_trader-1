import resource
import select
import socket
import json
import threading
import queue
import random
import os
from dotenv import load_dotenv
load_dotenv()
BUFFER_SIZE = 4096
next_server_index = [0]
STUBBED = False

class Server:
    def __init__(self, ip_addr, port):
        self.ip_addr = ip_addr
        self.port = port
        self.socket_pool = []

    def connect_socket(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect((self.ip_addr, self.port))
        self.socket_pool.append(_socket)
        return _socket

    def close_all_sockets(self):
        sockets = self.socket_pool
        for _socket in sockets:
            _socket.close()
            sockets.remove(_socket)

    def close_socket(self, _socket):
        try:
            if (_socket):
                _socket.shutdown(socket.SHUT_RDWR)
                _socket.close()
                self.socket_pool.remove(_socket)
                del _socket
        except OSError as e:
            print(e)

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
        try:
            if STUBBED:
                self.workload_conn.sendall(str.encode(self.message))
                return
            print("\033[1;34m----\033[0;0m")
            print(f"\033[1;34mconnecting to {self.server}\033[0;0m")
            self.server_socket = self.server.connect_socket()
            print("\033[1;34msending:\033[0;0m")
            print(f"\033[1;34m{self.message}\033[0;0m")
            self._send(self.message)
            print("\033[1;34msent! waiting on response...\033[0;0m")
            response_bytes = self._recvall()
            if (response_bytes != None and len(response_bytes) > 0):
                print(f"\033[1;34mreceived response\033[0;0m")
                # print(response)
                print("\033[1;34msending back to client...\033[0;0m")
                self.workload_conn.sendall(response_bytes)
                print("\033[1;34msent!\033[0;0m")

            else:
                print("\033[1;2;33mno response, closing socket....\033[0;0m")
                # self.server.close_socket(self.server_socket)
                print("\033[1;2;33msocket closed\033[0;0m")
            self.server.close_socket(self.server_socket)
            print("\033[1;34m----\033[0;0m")
        except Exception as e1:
            print(f"\033[1;31mLD_BAL.run:{e1}\033[0;0m")

    def _send(self, data):
        self.server_socket.sendall(str.encode(data))

    def _recv(self):
        return self.server_socket.recv(BUFFER_SIZE).decode()

    def _recvall(self):
        # Helper function to recv all bytes from response
        # Must have server side close connection when finished to ensure EOF is caught on this end.
        data = bytearray()
        while True:
            try:
                packet = self.server_socket.recv(BUFFER_SIZE)
                if len(packet) < BUFFER_SIZE:
                    data.extend(packet)
                    break
                data.extend(packet)
            except Exception as e2:
                print(f"\033[1;31mLoad_Bal.recvall:{e2}\033[0;0m")
        return data

def terminate_servers_sockets():
    [server.close_all_sockets() for server in servers]

class ConnectionPool:
    def __init__(self):
        self.pool = []
    def new_connection(self, server, workload_conn, incoming_message):
        connection_thread = ConnectionThread(server, workload_conn, incoming_message)
        connection_thread.start()
        self.pool.append(connection_thread)
    def __repr__(self):
        string = "---------------\nconnection pool: \n"
        for conn in self.pool:
            string = string + "\n" + str(conn.is_alive())
        return string + "\n---------------\n"
        
def users_distribution_report():
    user_ids = users.keys()
    distribution = {}
    for user_id in user_ids:
        server = users[user_id]
        distribution[user_id] = str(server)
    return json.dumps(distribution)

def get_next_available_server():
    # round robin
    next_server_index[0] = (next_server_index[0] + 1) % len(servers)
    return servers[next_server_index[0]]

def assign_random_server():
    return servers[random.randint(0, len(servers) - 1)]

def set_user_relay(username):
    if STUBBED: return None
    if (username == None):
        server = assign_random_server()
    else:
        try:
            server = users[username]
        except KeyError:
            server = get_next_available_server()
            users[username] = server
            print(f"\033[1;34mLB.set_user_relay:{username} assigned to server: {str(server)}\033[0;0m")
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

def launch(work_gen_portal, conn_pool):
    open_sockets = [work_gen_portal]
    try:
        while True:
            print(f"\033[1;31mnum_socks: {len(open_sockets)}\033[0;0m")
            readable, writable, exceptional = select.select(open_sockets, [], [])
            for s in readable:
                if s is work_gen_portal:
                    wg_conn, wg_addr = work_gen_portal.accept()
                    open_sockets.append(wg_conn)
                else:
                    try:
                        incoming_message = s.recv(BUFFER_SIZE).decode()
                        if len(incoming_message) > 0:
                            username = get_username(incoming_message)
                            server = set_user_relay(username)
                            conn_pool.new_connection(server=server, workload_conn=s, incoming_message=incoming_message)
                        else:
                            s.shutdown(socket.SHUT_RDWR)
                            s.close()
                            open_sockets.remove(s)
                    except Exception as e1:
                        print(f"error: {e1}")
                        pass
    except Exception as e2:
        for s in open_sockets:
            s.shutdown(socket.SHUT_RDWR)
            s.close()
        print(f"\033[1;31mLB.launch, error: {e2}\033[0;0m")
        exit()

if __name__ == "__main__":
    load_balancer_host = os.environ.get("load_balancer_host")
    load_balancer_port = int(os.environ.get("load_balancer_port"))
    try:
        workload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        workload_socket.bind((load_balancer_host, load_balancer_port))
        workload_socket.listen(1500)
        print(f"\033[1;34mload balancer service running on {load_balancer_host}:{load_balancer_port}...\033[0;0m")
        connection_pool = ConnectionPool()
        launch(workload_socket, connection_pool)
        # while True:
        #     workload_conn, addr = workload_socket.accept()
        #     incoming_message = workload_conn.recv(BUFFER_SIZE).decode()
        #     if len(incoming_message) > 0:
        #         username = get_username(incoming_message)
        #         server = set_user_relay(username)
        #         connection_pool.new_connection(server=server, workload_conn=workload_conn, incoming_message=incoming_message)
        #     print(f"\033[1;35mLD_BAL-wrk_gen_socks:{len(users)} | web_srv_socks:{len(servers)} | threads:{threading.active_count()}\033[0;0m")
    except Exception as e:
        print(f"\033[1;31mLB.main:{type(e)} | \033[0;0m", end="")
        print(f"\033[1;31m{e}\033[0;0m")
    finally:
        print("\n\033[1;34m" + "distribution report:\033[0;0m")
        print(users_distribution_report())
        terminate_servers_sockets()
