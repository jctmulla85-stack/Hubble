import json
import datetime
from collections import defaultdict

class EventBus:
    def __init__(self, log_path="trading_audit.log"):
        self.handlers = defaultdict(list)
        self.log_path = log_path

    def subscribe(self, event_type, handler):
        self.handlers[event_type].append(handler)

    def publish(self, event_type, payload):
        event = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "type": event_type,
            "payload": payload
        }
        # Permanent Audit Trail
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")

        # Route to subscribers
        for handler in self.handlers.get(event_type, []):
            handler(event)
