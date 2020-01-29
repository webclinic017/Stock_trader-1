from client_data import ClientData
from transaction_server import TransactionServer
from quote_cache import QuoteCache
from event_server import EventServer


# Launches a TransactionServer
def main():
    cd = ClientData()
    es = EventServer()
    qc = QuoteCache("quoteserve.seng.uvic.ca", 4444)
    es.give_hooks(cd, qc)
    # server = TransactionServer(cd, qc, es, "192.168.1.178", (44415, 44420))
    server = TransactionServer(cd, qc, es, "127.0.0.1", (44415, 44420))
    server.launch()


if __name__ == "__main__":
    main()
