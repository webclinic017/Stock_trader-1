
import xml.etree.ElementTree as elementTree
import uuid
import time
import json
server_name = "audit_log_server"
class logger:
    def __init__(self):
        self._audit_log = {}
        self._transaction_num = 0
    
    def get_current_transaction_num(self):
        return self._transaction_num

    def get_next_transaction_num(self):
        transaction_num = self._transaction_num
        transaction_num = transaction_num + 1
        self._transaction_num = transaction_num
        return transaction_num

    def insert_log(self, data):
        print("incoming log data:")
        print(data)
        audit_log = self._audit_log
        response = {"status": "ERROR"}

        log_key = list(data.keys())[0]
        log = data[log_key]
        audit_log[log_key] = {
            "commandType": log["commandType"],
            "data_fields": {}
        }
        fields = log["data_fields"].keys()
        for field in fields:
            value = log["data_fields"][field]
            audit_log[log_key]["data_fields"][field] = value
        response["status"] = "SUCCESS"
        self._audit_log = audit_log

        return response

    def get_logs(self, data):
        try:
            data = json.loads(data)
        except TypeError:
            pass
        audit_log = self._audit_log
        print("dumplog")
        response = {"status": "ERROR"}
        self._log_dumplog(data)
        logs_root = elementTree.Element("log")
        log_keys = audit_log.keys()
        log_i = 0
        for log_key in log_keys:
            log = audit_log[log_key]
            data_fields = log["data_fields"].keys()
            data_field_elements = []
            for data_field in data_fields:
                value = log["data_fields"][data_field]
                log_element = elementTree.Element(log["commandType"])
                data_field_element = elementTree.Element(data_field)
                data_field_element.text = str(value)
                data_field_elements.append(data_field_element)
            log_element.extend(data_field_elements)
            logs_root.append(log_element)
            log_i = log_i + 1
        xml_string = (elementTree.tostring(logs_root, encoding='utf-8')).decode('utf-8')
        response["status"] = "SUCCESS"
        response["data"] = xml_string
        return response

    def debug(self):
        print("current state of audit_log dict:")
        print(self._audit_log)  
        return self._audit_log  

    def _log_dumplog(self, data):
        # log the dumplog command
        audit_dump_log_entry = {}
        log_key = str(uuid.uuid4())
        audit_dump_log_entry[log_key] = {
            "commandType": "userCommand",
            "data_fields": {
                "transactionNum": self.get_next_transaction_num(),
                "timestamp": int(time.time() * 1000),
                "filename": data["filename"],
                "command": "DUMPLOG",
                "server": server_name
            }
        }
        try:
            audit_dump_log_entry["data_fields"]["username"] = data["userid"]
        except KeyError:
            pass
        self.insert_log(audit_dump_log_entry)