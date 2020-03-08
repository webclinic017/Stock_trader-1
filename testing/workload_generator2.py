import math
import sys
import time
import os
import requests
from multiprocessing import Process, Pool, Queue, Pipe
import threading
from enum_utils import CommandURLs

# command line usage: "py workload_generator.py --1"
# Where '--1' is the workload file to use as stated below

workload_paths = {
    "--1": "./workload_files/1userWorkLoad.txt",
    "--2": "./workload_files/2userWorkLoad.txt",
    "--10": "./workload_files/10User_testWorkLoad.txt",
    "--45": "./workload_files/45User_testWorkLoad.txt",
    "--100": "./workload_files/100User_testWorkLoad.txt",
    "--1000": "./workload_files/1000User_testWorkLoad.txt",
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
    "--2_test": "./workload_files/2user_test.txt",
    "--4_test": "./workload_files/4user_test.txt"
}

base_url = "http://127.0.0.1:5000"


class UserThread(threading.Thread):
    def __init__(self, name, args: tuple):
        super().__init__(name=name)
        self.name = name
        self.args = args

    def run(self):
        forward_requests(self.name, self.args[0], self.args[1])


def process_dumplog(output_filename, dumplog_response):
    try:
        xml_string = dumplog_response.json()["data"]
        with open(output_filename, 'w+') as f:
            f.write(xml_string)
    except KeyError:
        print(f"Error: no data attribute found in response. Response status {dumplog_response.json()['status']}")


# Read work load file, process into a dictionary of user command lists that can be run in parallel:
# e.g. {"user1": [all commands for user1], "user2": [all commands for user2]}
# noinspection PyPep8Naming
def workload_to_user_command_dicts(file_obj):
    user_divided_commands = {}
    client_actions_raw = [line.rstrip().split()[-1].split(",") for line in file_obj]
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
                if len(action) == 3:
                    filenameIndex = 2
                    usernameIndex = 1
                next_command["filename"] = action[filenameIndex]
                if usernameIndex is not None:
                    username = action[usernameIndex]
                    next_command["userid"] = username
                    if username in user_divided_commands:
                        user_divided_commands[username].append(next_command)
                    else:
                        user_divided_commands[username] = [next_command]
                elif "admin" in user_divided_commands:
                    user_divided_commands["admin"].append(next_command)
                else:
                    user_divided_commands["admin"] = [next_command]
            else:
                print(f"Invalid command: #{i + 1} -> {action}")
                continue
        except Exception as e:
            print(f"{e} | {action}")
            continue

        if command == "DUMPLOG":
            continue
        elif action[1] in user_divided_commands:
            user_divided_commands[action[1]].append(next_command)
        else:
            user_divided_commands[action[1]] = [next_command]

    return user_divided_commands

# Creates a thread for each set of user requests, runs all created threads, assembles and returns responses
def process_user_requests(request_sets, main_pipe):
    # Create the user threads
    user_threads = []
    for usr_idx, user_requests in enumerate(request_sets):
        a, b = Pipe()
        thread = UserThread(name=f"{os.getpid()}|{usr_idx}", args=(user_requests, b))
        user_threads.append((thread, (a, b)))
        thread.start()

    # Wait for all threads to finish
    responses = []
    for t in user_threads:
        t[0].join()             # Halt main thread until all threads are complete
        t[1][1].close()         # Close pipe
        # resp = t[1][0].recv()   # Receive responses from the closed pipe
        # responses.append(resp)  # Append responses to the main response list

    # Send back list of lists of responses
    main_pipe.send(responses)
    print(f"num user response sets:{len(responses)}")

# Forwards requests for a single user to the web servers(or load balancer), returns responses
def forward_requests(thread_name, user_requests, user_pipe):
    session = requests.session()
    responses = []
    for idx, user_request in enumerate(user_requests):
        try:
            print(f"-->In:{idx + 1} | pid|thr:{thread_name}")
            response = session.post((base_url + CommandURLs[user_request["Command"]].value), data=user_request).json()
            responses.append(response)
            print(f"<--Out:{idx + 1} | pid|thr:{thread_name}")
            # print(f"{idx + 1} | {thread_name} | {response}")
        except Exception as e:
            print(f"{e} | {user_request}")
    print(f"finished:{thread_name}")
    # user_pipe.send(responses)
    # user_pipe.close()


if __name__ == "__main__":
    startT = time.time()
    file_index = sys.argv[1]
    file_object = open(workload_paths[file_index])
    user_cmd_dict = workload_to_user_command_dicts(file_object)
    admin_dumplog = user_cmd_dict.pop("admin", None)[0]
    user_cmd_dict_list = list(user_cmd_dict.values())
    num_users = len(user_cmd_dict_list)

    # The lab computers are dual core. Should use threading beyond this to simulate multiple active users.
    processes_to_create = 2
    users_on_first_process = math.ceil(num_users / processes_to_create)
    users_on_second_process = num_users - users_on_first_process
    print(f"num_users:{num_users}")

    a1, b1 = Pipe()
    a2, b2 = Pipe()
    l1 = user_cmd_dict_list[:users_on_first_process]
    l2 = user_cmd_dict_list[users_on_first_process:]
    p1 = Process(target=process_user_requests, args=(l1, b1))
    p2 = Process(target=process_user_requests, args=(l2, b2))

    # Start the processes
    p1.start()
    p2.start()
    # Halt main process until both sub-processes finish
    p1.join()
    p2.join()

    # TODO: Need to fix the pipe so we can analyze returned data
    # b1.close()
    # b2.close()
    # resps1 = a1.recv()
    # resps2 = a2.recv()
    # num_resps = 0
    # for element in resps1:
    #     num_resps += len(element)
    # for element in resps2:
    #     num_resps += len(element)
    # print(f"Total number responses:{num_resps}")

    endT = time.time()
    print(f"runtime: {endT - startT}")

    if admin_dumplog is not None:
        try:
            print(f"Printing dumplog!")
            server_response = requests.post((base_url + CommandURLs["DUMPLOG"].value), data=admin_dumplog)
            process_dumplog(admin_dumplog["filename"], server_response)
        except KeyError:
            pass
