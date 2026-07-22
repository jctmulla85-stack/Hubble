import sys
import os
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
# Ensure .env is in the same directory as this script
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 2. Add the project root to path for module discovery
PROJECT_ROOT = '/home/Mulla85/QuantBot'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 3. Import and Run
from communication.discord_notifier import send_alert

print("--- Discord Notification Test ---")
try:
    # This will now look for DISCORD_WEBHOOK_URL loaded by load_dotenv()
    send_alert("System Heartbeat: Connection successful.", level="info")
    print("SUCCESS: Alert sent to Discord.")
except Exception as e:
    print(f"FAILED: {e}")
