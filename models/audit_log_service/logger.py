
import xml.etree.ElementTree as elementTree
import uuid
import time
import json
import redis
import re
from heapq import heappush, heappop
server_name = "audit_log_server"

class logger:
    def __init__(self, redis_host, redis_port):
        self.r = redis.Redis(host=redis_host, port=redis_port, db=0)

    def increment_transaction_num(self):
        transaction_num = self.get_next_transaction_num()
        self.r.set("transactionNum", str(transaction_num))

    def get_current_transaction_num(self):
        reply = self.r.get("transactionNum")
        if (reply == None):
            transaction_num = 0
        else:
            transaction_num = int(reply)
        return transaction_num

    def get_next_transaction_num(self):
        transaction_num = int(self.get_current_transaction_num())
        transaction_num = transaction_num + 1
        return transaction_num

    def insert_log(self, data):
        print("incoming log data:")
        print(data)
        response = {"status": "ERROR"}

        log_key = list(data.keys())[0]
        commandType = data[log_key]["commandType"]
        try:
            username = data[log_key]["data_fields"]["username"]
        except KeyError:
            try:
                username = data[log_key]["userid"]
            except KeyError:
                username = ""
        transactionNum = data[log_key]["data_fields"]["transactionNum"]
        transactionNum_username_logId = f"{transactionNum}_{username}_{log_key}"
        r = self.r
        r.hset(transactionNum_username_logId, "commandType", commandType)
        log = data[log_key]
        for data_field in log["data_fields"].items():
            field = data_field[0]
            value = data_field[1]
            r.hset(transactionNum_username_logId, field, value)
        response["status"] = "SUCCESS"
        return response

    def get_logs(self, data):
        try:
            data = json.loads(data)
        except TypeError:
            pass
        print("dumplog")
        response = {"status": "ERROR"}
        self._log_dumplog(data)
        logs_root = elementTree.Element("log")
        log_i = 0
        matching_keys = []
        try:
            username = data["userid"]
        except KeyError:
            username = "**" # wildcard pattern to match for all entries
        matchStr = f"**_{username}_**"
        scan_iterator = self.r.scan_iter(match=matchStr)
        while (True):
            try:
                matching_key = str(next(scan_iterator), encoding='utf-8')
                trans_num = int(matching_key.split("_")[0])
                heappush(matching_keys, (trans_num, matching_key))
            except StopIteration:
                break
        pattern = re.compile("(.*)_(.*)_(.*)")
        try:
            while (True):
                key = heappop(matching_keys)[1]
                if (not pattern.match(key)):
                    continue
                log = self.r.hgetall(key)
                commandType = str(log[list(log.keys())[0]], encoding='utf-8')
                del log[list(log.keys())[0]]
                data_field_elements = []
                for data_field in log.items():
                    field = str(data_field[0], encoding='utf-8')
                    value = str(data_field[1], encoding='utf-8')
                    log_element = elementTree.Element(commandType)
                    data_field_element = elementTree.Element(field)
                    data_field_element.text = value
                    data_field_elements.append(data_field_element)
                log_element.extend(data_field_elements)
                logs_root.append(log_element)
                log_i = log_i + 1
        except IndexError:
            pass
        xml_string = (elementTree.tostring(logs_root, encoding='utf-8')).decode('utf-8')
        response["status"] = "SUCCESS"
        response["data"] = xml_string
        return response

    def _log_dumplog(self, data):
        # log the dumplog command
        audit_dump_log_entry = {}
        try:
            username = data["userid"]
        except KeyError:
            username = ""
        transaction_num = self.get_next_transaction_num()
        log_key = str(transaction_num) + "_" + username + "_" + str(uuid.uuid4())
        audit_dump_log_entry[log_key] = {
            "commandType": "userCommand",
            "data_fields": {
                "transactionNum": transaction_num,
                "timestamp": int(time.time() * 1000),
                "filename": data["filename"],
                "command": "DUMPLOG",
                "server": server_name
            }
        }
        if (len(username) > 0):
            audit_dump_log_entry[log_key]["data_fields"]["username"] = username
        self.insert_log(audit_dump_log_entry)
        self.increment_transaction_num()