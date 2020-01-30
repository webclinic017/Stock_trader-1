
import xml.etree.ElementTree as elementTree
audit_log = {}

class logger:
    def insert_log(self, data):
        response = {"status": "ERROR"}
        try:
            log_key = data["username"] + "_" + data["transactionId"]
            audit_log[log_key] = {}
            audit_log[log_key]["data_fields"] = {}
            audit_log[log_key]["data_fields"]["username"] = data["username"]
            audit_log[log_key]["data_fields"]["transactionId"] = data["transactionId"]
            audit_log[log_key]["type"] = data["type"]
            fields = data["data_fields"].keys()
            for field in fields:
                value = data["data_fields"][field]
                audit_log[log_key]["data_fields"][field] = value
            response["status"] = "SUCCESS"
        except Exception as e:
            print(e)
        return response

    def get_logs(self):
        response = {"status": "ERROR"}
        logs_xml = elementTree.Element('?xml version="1.0"?')
        logs_root = elementTree.Element("log")
        log_keys = audit_log.keys()
        for log_key in log_keys:
            log = audit_log[log_key]
            elementTree.SubElement(logs_root, log["type"])
            data_fields = log["data_fields"].keys()
            for data_field in data_fields:
                value = log["data_fields"][data_field]
                data_field_element = elementTree.SubElement(logs_root, data_field)
                data_field_element.text = str(value)
        xml_string = (elementTree.tostring(logs_xml, encoding='utf-8') + elementTree.tostring(logs_root, encoding='utf-8')).decode('utf-8')
        response["status"] = "SUCCESS"
        response["data"] = xml_string
        return response
