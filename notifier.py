import requests
import json

# Replace with your actual Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1524756805039951944/pou04Te3B0E3_yYsQj4wDYM_orjnEfaCbRvCBadf7G47P1iEcLksUUK-Pkf4c2aXkzeY"

def send_alert(message):
    data = {"content": message}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

# Example usage:
# send_alert("✅ Reconciliation Complete: System Balanced.")
