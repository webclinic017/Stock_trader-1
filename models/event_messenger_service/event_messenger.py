import redis
import json
import uuid
import re
import threading

class event_messenger:
    # pending indicates that the event has not yet been fulfilled (the stock has not reached the buy or sell amount yet)
    PENDING = "pending"

    # ready indicates that the stock quote satisfies the buy or sell amount of the trigger, and is ready to be fulfilled by the transaction server
    READY = "ready"

    # fulfilled indicates that the event has been fulfilled by the transaction server, and should be removed
    FULFILLED = "fulfilled"

    class EventTypes:
        BUY = "buy"
        SELL = "sell"

    def __init__(self, redis_host, redis_port):
        self.r = redis.Redis(host=redis_host, port=redis_port)
        self.event_status_mutex = threading.Lock()

    def set_event(self, event_id, event_type, status, username, stock_symbol, target_dollars, target_cents):
        assert (event_type == EventTypes.BUY or event_type == EventTypes.SELL)
        key = f"{event_type}_{event_id}_{status}"

        self.r.hmset(key, {"event_id": event_id, "event_type": event_type, "status": status, "username": username, "stock_symbol": stock_symbol, "target_dollars": target_dollars, "target_cents": target_cents})
        return {"status": "SUCCESS", "event_id": event_id}

    def get_all_pending_events(self):
        match_str = f"**_**_{PENDING}"
        return self.get_all_matching_events(match_str)
    
    def get_all_matching_events(self, match_str, first_result=False):
        scan_iterator = self.r.scan_iter(match=match_str)
        matching_keys = []
        events = []
        while (True):
            try:
                matching_key = str(next(scan_iterator), encoding='utf-8')
                if (matching_key != None):
                    if (first_result):
                        return [self.r.hgetall(matching_key)]
                    matching_keys.append(matching_key)
            except StopIteration:
                break
        pattern = re.compile("(.*)_(.*)_(.*)")
        for key in matching_keys:
            if (not pattern.match(key)):
                continue
            event = self.r.hgetall(key)
            events.append(event)
        return events

    def set_event_status(self, event_id, new_status):
        self.event_status_mutex.acquire()
        try:
            event = self.get_all_matching_events(match_str=f"**_{event_id}_**", first_result=True)
            if (new_status == event["status"]):
                self.event_status_mutex.release()
                return {"status": "SUCCESS: no event status change necessary"}
            username = event["username"]
            event_id = event["event_id"]
            status = event["status"]
            key = f"{username}_{event_id}_{status}"

            # since the event status is embedded in the key, must delete the previous entry and add a new entry with the new status embedded in the key
            self.r.delete(key)
            response = self.set_event(
                event_id=event_id, 
                event_type=event["event_type"], 
                status=status, 
                username=username, 
                stock_symbol=event["stock_symbol"], 
                target_dollars=event["target_dollars"], 
                target_cents=event["target_cents"]
            )
        finally:
            self.event_status_mutex.release()
        return response

    def delete_event(self, key):
        self.r.delete(key)
        return {"status": "SUCCESS"}