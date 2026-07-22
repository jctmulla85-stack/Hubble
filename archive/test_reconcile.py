import sys
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# 1. Define paths and load environment
DOTENV_PATH = '/home/Mulla85/QuantBot/.env'
sys.path.append('/home/Mulla85/QuantBot')

if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
    print("SUCCESS: .env file found and loaded.")
else:
    print(f"CRITICAL ERROR: No .env file found at {DOTENV_PATH}")
    sys.exit()

# 2. Extract keys using the names defined in your .env
api_key = os.getenv('ALPACA_KEY_APEX_001')
secret_key = os.getenv('ALPACA_SECRET_APEX_001')

if not api_key or not secret_key:
    print("CRITICAL: Keys are empty in .env. Check your file.")
    sys.exit()
else:
    print("API Key found: Yes")

# 3. Initialize Client and Reconcile
try:
    # Authenticate
    api = TradingClient(api_key, secret_key, paper=True)

    # Import and execute your ground truth logic
    from execution.reconcile import get_live_truth

    print("--- Reconciliation (Ground Truth) Test ---")
    truth = get_live_truth(api)

    if truth:
        print("TEST PASSED: Successfully fetched Ground Truth from Broker.")
        print(f"Equity: {truth.get('equity')}")
    else:
        print("TEST FAILED: Function returned None. Check API permissions.")

except Exception as e:
    print(f"TEST FAILED: Error: {e}")
