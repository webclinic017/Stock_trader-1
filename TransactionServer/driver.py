from client_data import ClientData
from transaction_server import TransactionServer
from quote_cache import QuoteCache
from event_server import EventServer

# Launches a TransactionServer
def main():
	cd = ClientData()
	es = EventServer()
	qc = QuoteCache("quoteserve.seng.uvic.ca", 4444)
	es.give_quotecache(cd, qc)
	server = TransactionServer(cd, qc, "127.0.0.1", 4080)
	server.launch()

if __name__ == "__main__":
    main()
