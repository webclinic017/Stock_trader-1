import socket
import sys


# Simple client to debug TransactionServer
def main():
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect(("127.0.0.1", 44415))
	while True:
		print("Enter JSON command: ")
		command = sys.stdin.readline()
		conn.send(str.encode(command))
		command = conn.recv(1024).decode()
		print("Received: " + command + "\n")


if __name__ == "__main__":
	main()
