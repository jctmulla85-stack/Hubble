import json
import logging
import datetime

# Configure a JSON-ready file handler
audit_logger = logging.getLogger("AuditLog")
audit_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('audit_trail.jsonl') # JSON Lines format
audit_logger.addHandler(file_handler)

def log_event(event_type, details):
    """Logs an event as a structured JSON object."""
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "type": event_type,
        "data": details
    }
    audit_logger.info(json.dumps(event))
