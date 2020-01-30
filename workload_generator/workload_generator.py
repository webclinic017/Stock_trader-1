import json
import socket
import sys
import requests

# TODO: Connect with webserver (eventually a loadbalancer)
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(("192.168.0.15", 5000))

workload_paths = {
	"--1": "./workload_files/1userWorkLoad.txt",
	"--2": "./workload_files/2userWorkLoad.txt",
	"--10": "./workload_files/10User_testWorkLoad.txt",
	"--45": "./workload_files/45User_testWorkLoad.txt",
	"--100": "./workload_files/100User_testWorkLoad.txt",
	"--1000": "./workload_files/1000userWorkLoad.txt",
	"--2006": "./workload_files/final2006WorkLoad.txt",
	"--2007": "./workload_files/final2007.txt",
	"--2009": "./workload_files/final_workload_2009.txt",
	"--2010": "./workload_files/final_workload_spring_2010.txt",
	"--2011": "./workload_files/final_workload_2011.txt",
	"--2013": "./workload_files/final_workload_2013.txt",
	"--2014": "./workload_files/final_workload_2014.txt",
	"--2015": "./workload_files/final_workload_2015.txt",
	"--2016": "./workload_files/2016.txt",
	"--2017": "./workload_files/final_workload_2017.txt",
	"--2018": "./workload_files/final_workload_2018.txt",
	"--2019": "./workload_files/final_workload_2019.txt",
}

command_urls = {
	"ADD": "/addFunds",
	"QUOTE": "/getQuote",
	"BUY": "/buyStock",
	"COMMIT_BUY": "/commitBuy",
	"CANCEL_BUY": "/cancelBuy",
	"SELL": "/sellStock",
	"COMMIT_SELL": "/commitSell",
	"CANCEL_SELL": "/cancelSell",
	"SET_BUY_AMOUNT": "/setBuyAmount",
	"CANCEL_SET_BUY": "/cancelSetBuy",
	"SET_BUY_TRIGGER": "/setBuyTrigger",
	"SET_SELL_AMOUNT": "/setSellAmount",
	"SET_SELL_TRIGGER": "/setSellTrigger",
	"CANCEL_SET_SELL": "/cancelSetSell",
	"DUMPLOG": "/dumpLog",
	"DISPLAY_SUMMARY": "/displaySummary"
}

base_url = "http://127.0.0.1:5000"

# TODO: take in workload file index from command line args
file_index = sys.argv[1]
fileObject = open(workload_paths[file_index])

client_action = {
	"Command": "ADD",
	"userid": "treese",
	"amount": "1200"
}

# commands = [line.rstrip().split()[-1] for line in fileObject]
# print(commands)

server_response = requests.get(base_url + command_urls["ADD"], json=client_action)
print(server_response)

# s.sendall(str.encode(json.dumps(client_action)))
#
# # Receive response
# server_response = s.recv(1024).decode()
# print("--RESPONSE:" + str(server_response))

# TODO: process it once to capture all users and add them to the system with no stocks and $0.00 in funds

# TODO: process each command

def process_dumplog(output_filename, dumplog_response):
	try:
		xml_string = dumplog_response.json()["data"]
		with open(output_filename, 'w+') as f:
			f.write(xml_string)
	except KeyError:
		print(f"Error: no data attribute found in response. Response status {dumplog_response.json()['status']}")

