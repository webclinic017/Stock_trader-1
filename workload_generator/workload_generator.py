import sys
import requests

# command line usage: "py workload_generator.py --1"
# Where '--1' is the workload file to use as stated below
rootFolder = ""

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

def process_dumplog(output_filename, dumplog_response):
	try:
		xml_string = dumplog_response.json()["data"]
		with open(output_filename, 'w+') as f:
			f.write(xml_string)
	except KeyError:
		print(f"Error: no data attribute found in response. Response status {dumplog_response.json()['status']}")

base_url = "http://127.0.0.1:5000"
file_index = sys.argv[1]
try:
	rootFolder = f"{sys.argv[2]}/"
except IndexError:
	rootFolder = ""

workload_paths = {
	"--1": f"./{rootFolder}workload_files/1userWorkLoad.txt",
	"--2": f"./{rootFolder}workload_files/2userWorkLoad.txt",
	"--10": f"./{rootFolder}workload_files/10User_testWorkLoad.txt",
	"--45": f"./{rootFolder}workload_files/45User_testWorkLoad.txt",
	"--100": f"./{rootFolder}workload_files/100User_testWorkLoad.txt",
	"--1000": f"./{rootFolder}workload_files/1000User_testWorkLoad.txt",
	"--2006": f"./{rootFolder}workload_files/final2006WorkLoad.txt",
	"--2007": f"./{rootFolder}workload_files/final2007.txt",
	"--2009": f"./{rootFolder}workload_files/final_workload_2009.txt",
	"--2010": f"./{rootFolder}workload_files/final_workload_spring_2010.txt",
	"--2011": f"./{rootFolder}workload_files/final_workload_2011.txt",
	"--2013": f"./{rootFolder}workload_files/final_workload_2013.txt",
	"--2014": f"./{rootFolder}workload_files/final_workload_2014.txt",
	"--2015": f"./{rootFolder}workload_files/final_workload_2015.txt",
	"--2016": f"./{rootFolder}workload_files/2016.txt",
	"--2017": f"./{rootFolder}workload_files/final_workload_2017.txt",
	"--2018": f"./{rootFolder}workload_files/final_workload_2018.txt",
	"--2019": f"./{rootFolder}workload_files/final_workload_2019.txt",
}

fileObject = open(workload_paths[file_index])

b = {"Command": "ADD", "userid": "treese", "amount": "1200"},

# Read work load file, process into dict commands
client_actions_raw = [line.rstrip().split()[-1].split(",") for line in fileObject]
client_actions = []
for i, action in enumerate(client_actions_raw):
	command = action[0]
	next_command = {"Command": command}
	try:
		if command == "ADD":
			next_command["userid"] = action[1]
			next_command["amount"] = action[2]
		elif command == "QUOTE":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
		elif command == "BUY":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
			next_command["amount"] = action[3]
		elif command == "COMMIT_BUY":
			next_command["userid"] = action[1]
		elif command == "CANCEL_BUY":
			next_command["userid"] = action[1]
		elif command == "SELL":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
			next_command["amount"] = action[3]
		elif command == "COMMIT_SELL":
			next_command["userid"] = action[1]
		elif command == "CANCEL_SELL":
			next_command["userid"] = action[1]
		elif command == "SET_BUY_AMOUNT":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
			next_command["amount"] = action[3]
		elif command == "CANCEL_SET_BUY":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
		elif command == "SET_BUY_TRIGGER":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
			next_command["amount"] = action[3]
		elif command == "SET_SELL_AMOUNT":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
			next_command["amount"] = action[3]
		elif command == "CANCEL_SET_SELL":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
		elif command == "SET_SELL_TRIGGER":
			next_command["userid"] = action[1]
			next_command["StockSymbol"] = action[2]
			next_command["amount"] = action[3]
		elif command == "DISPLAY_SUMMARY":
			next_command["userid"] = action[1]
		elif command == "DUMPLOG":
			filenameIndex = 1
			usernameIndex = None
			if (len(action) == 3):
				filenameIndex = 2
				usernameIndex = 1
			next_command["filename"] = action[filenameIndex]
			if (usernameIndex != None):
				next_command["userid"] = action[usernameIndex]
		else:
			print(f"Invalid command: #{i+1} -> {action}")
			continue
	except Exception as e:
		print(f"{e} | {action}")
		continue

	# TEMPORARY: for dumplog development--------
#	audit_log_server_ip = "localhost"  # IP on home comp
#	audit_log_server_port = 44416
#	protocol = "http"
#	from AuditLogBuilder import AuditLogBuilder
#	import json
#	server_name = "someserver"
#	request_dict1 = json.dumps({
#		"Command": "ADD",
#		"userid": "someUserGuy",
#		"amount": 100.10
#	})
#	AuditLogBuilder("ADD", server_name).build(request_dict1).send(protocol, audit_log_server_ip, audit_log_server_port)
#	request_dict2 = json.dumps({
#		"Command": "ADD",
#		"userid": "someUserGuy2",
#		"amount": 100.10
#	})
#	AuditLogBuilder("ADD", server_name).build(request_dict2).send(protocol, audit_log_server_ip, audit_log_server_port)
#	#-------------------------------------------

	server_response = requests.post((base_url + command_urls[command]), data=next_command)
	print(f"#{i+1} action:{action} response:{server_response}")

	try:
		process_dumplog(next_command["filename"], server_response)
	except KeyError:
		pass
