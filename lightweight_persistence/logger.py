
import xml.etree.ElementTree as elementTree
import uuid
class logger:
    def __init__(self):
        self._audit_log = {}

    def debug(self):
        print("current state of audit_log dict:")
        print(self._audit_log)  
        return self._audit_log  
    
    def insert_log(self, data):
        print("incoming log data:")
        print(data)
        audit_log = self._audit_log
        response = {"status": "ERROR"}
        try:
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
        except Exception as e:
            print(e)
        return response

    def get_logs(self):
        audit_log = self._audit_log
        print("dumplog")
        print(self._audit_log)
        transactionNum = 1
        response = {"status": "ERROR"}
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
            transaction_num_field = elementTree.SubElement(log_element, "transactionNum")
            transaction_num_field.text = str(transactionNum)
            transactionNum = transactionNum + 1
            log_element.extend(data_field_elements)
            logs_root.append(log_element)
            log_i = log_i + 1
        xml_string = (elementTree.tostring(logs_root, encoding='utf-8')).decode('utf-8')
        response["status"] = "SUCCESS"
        response["data"] = xml_string

        # log the dumplog command
        audit_dump_log_entry = {}
        audit_dump_log_entry[str(uuid.uuid4())] = {
            "commandType": "userCommand",
            "data_fields": {
                "command": "DUMPLOG"
            }
        }
        self.insert_log(audit_dump_log_entry)

        return response
