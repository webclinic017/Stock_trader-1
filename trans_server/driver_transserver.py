print("starting trans server")

from client_data import ClientData
from transaction_server import TransactionServer
from quote_cache import QuoteCache
from event_server import EventServer
import argparse, sys

print("starting trans server")

protocol = "http"
server_name = "transaction server"
transaction_server_ip = "localhost"
transaction_server_port = 5000
user_db_host = "localhost"
user_db_port = 5001
quote_cache_host = "localhost"
quote_cache_port = 5002
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--QuoteServer", "-qs", type=int, default=0, help="set to 0 to indicate if quote server connection is not available (should be stubbed out), default value is 1 (expects real quote server to connect to)")

if __name__ == "__main__":
    print("first line")
    cd = ClientData(server_name=server_name, protocol=protocol, user_db_host=user_db_host, user_db_port=user_db_port)
    
    es = EventServer()

    should_stub_quote_server = not arg_parser.parse_args().QuoteServer
    qc = QuoteCache("quoteserve.seng.uvic.ca", 4444, should_stub=should_stub_quote_server, server_name=server_name, protocol=protocol, quote_cache_host=quote_cache_host, quote_cache_port=quote_cache_port)
    
    es.give_hooks(cd, qc)

    print("server ip = " + str(transaction_server_ip))
    print("server port = " + str(transaction_server_port))
    server = TransactionServer(cd, qc, es, transaction_server_ip, transaction_server_port, server_name=server_name)

    print("server up!!")
    server.launch()