
from client_data import ClientData
from transaction_server import TransactionServer
from quote_cache import QuoteCache
from event_server import EventServer

protocol = "http"
server_name = "transaction server"

if __name__ == "__main__":
    cd = ClientData(server_name=server_name, protocol=protocol)
    es = EventServer()
    qc = QuoteCache(server_name=server_name, protocol=protocol)
    es.give_hooks(cd, qc)
    server = TransactionServer(cd, qc, es, server_name=server_name)
    server.launch()