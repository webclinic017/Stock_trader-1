# python script for starting up the Stock Trader microservices for development

import sys
import subprocess
import argparse
import os
import time
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--QuoteServer", "-qs", type=int, default=0, help="set to 0 to indicate if quote server connection is not available (should be stubbed out), default value is 1 (expects real quote server to connect to)")
subprocesses = []

def start_service(path_to_entrypoint, script_args=[]):
    python_executable = sys.executable
    p_args = [python_executable, path_to_entrypoint]
    for arg in script_args:
        p_args.append(arg)
    subprocesses.append(subprocess.Popen(p_args))

def cleanup():
    for p in subprocesses:
        p.terminate()

if __name__ == "__main__":
    try:
        parsed_args = arg_parser.parse_args()
        start_service("models/audit_log_service/logger_api.py")
        start_service("models/user_model/user_api.py")
        start_service("models/quote_cache/quote_cache_api.py")
        #start_service("models/events_service/events_api.py")
        start_service("trans_server/driver_transserver.py", ["--QuoteServer", str(parsed_args.QuoteServer)])
        start_service("web_server/driver_webserver.py")

        #TODO: Use something other than an endless loop to keep subprocesses alive
        while (True):
            try:
                time.sleep(5)
                pass
            except KeyboardInterrupt:
                cleanup()
    except Exception as e:
        print(e)
        cleanup()