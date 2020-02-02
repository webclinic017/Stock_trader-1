from client_data import ClientData
from transaction_server import TransactionServer
from quote_cache import QuoteCache
from event_server import EventServer
import argparse, sys


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--QuoteServer", "-qs", type=int, default=1, help="set to 0 to indicate if quote server connection is not available (should be stubbed out), default value is 1 (expects real quote server to connect to)")

if __name__ == "__main__":
    cd = ClientData()
    es = EventServer()

    should_stub_quote_server = not arg_parser.parse_args().QuoteServer
    qc = QuoteCache("quoteserve.seng.uvic.ca", 4444, should_stub=should_stub_quote_server)
    es.give_hooks(cd, qc)
    server = TransactionServer(cd, qc, es, "127.0.0.1", 44415)
    server.launch()