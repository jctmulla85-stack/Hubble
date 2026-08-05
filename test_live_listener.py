import os
import time
from execution_core import ExecutionCore

def verify_live_listener():
    print("=== INITIALIZING LIVE LISTENER DRY-RUN ===")
    core = ExecutionCore()
    
    # Test connection and fetch account status to ensure API credentials & market connectivity work
    try:
        account = core.client.get_account()
        print(f"API CONNECTION SUCCESS: Status -> {account.status}")
        print(f"Buying Power: ${float(account.buying_power):,.2f}")
        print(f"Cash: ${float(account.cash):,.2f}")
    except Exception as e:
        print(f"API CONNECTION ERROR: {e}")
        return

    # Simulate a dry-run test signal execution through the supervisor gatekeeper
    print("\n[Testing Gatekeeper & Risk Interlocks with dummy signal]")
    test_result = core.execute_signal("AAPL", 10, "buy", 150.0)
    print(f"Dry-run Signal Routing Result: {test_result}")
    print("=== LIVE LISTENER DRY-RUN COMPLETE ===")

if __name__ == "__main__":
    verify_live_listener()
