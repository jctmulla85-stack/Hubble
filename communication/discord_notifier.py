import os
import requests

def send_alert(message, level="info"):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not set in environment")
        return

    payload = {"content": f"[{level.upper()}] {message}"}
    requests.post(webhook_url, json=payload)
