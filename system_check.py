import os
import sys
import logging
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient

def run_check():
    print("=== [SYSTEMS CHECK] Starting Diagnostic ===")
    
    # 1. Environment Variable Check
    api_key = os.getenv("ALPACA_KEY_APEX_001")
    secret_key = os.getenv("ALPACA_SECRET_APEX_001")
    if not api_key or not secret_key:
        print("[FAIL] Alpaca API keys are missing from environment variables.")
        sys.exit(1)
    else:
        print("[PASS] Alpaca API keys loaded successfully.")

    # 2. API Connectivity Check
    try:
        trading_client = TradingClient(api_key, secret_key, paper=True)
        account = trading_client.get_account()
        print(f"[PASS] Connected to Alpaca Paper API. Account Status: {account.status}, Buying Power: {account.buying_power}")
    except Exception as e:
        print(f"[FAIL] Failed connecting to Alpaca API: {e}")
        sys.exit(1)

    # 3. Component Modules Import Check
    try:
        import engine
        import volatility_guard
        import order_executor
        import asset_loader
        import production_runner
        print("[PASS] All custom modules imported successfully.")
    except ImportError as e:
        print(f"[FAIL] Module import error: {e}")
        sys.exit(1)

    # 4. Ledger File Check
    if os.path.exists("trading_engine_ledger.log"):
        print("[PASS] Trading ledger log file is present.")
    else:
        print("[INFO] Trading ledger log file will be created on first run.")

    print("=== [SYSTEMS CHECK] All Systems Nominal ===")

if __name__ == "__main__":
    run_check()
