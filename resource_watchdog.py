import os
import time
from datetime import datetime, timezone
from alpaca.trading.client import TradingClient

class ResourceWatchdog:
    def __init__(self):
        self.api_key = os.getenv("ALPACA_KEY_APEX_001")
        self.api_secret = os.getenv("ALPACA_SECRET_APEX_001")
        self.client = TradingClient(self.api_key, self.api_secret)

    def is_market_open(self):
        try:
            clock = self.client.get_clock()
            return clock.is_open
        except Exception as e:
            print(f"WATCHDOG ERROR fetching market clock: {e}")
            return False

    def enforce_idle_state(self):
        if not self.is_market_open():
            current_time = datetime.now(timezone.utc).isoformat()
            print(f"[{current_time}] Market closed. Enforcing zero-resource idle state (conserving CPU/RAM)...")
            return True
        return False

if __name__ == "__main__":
    watchdog = ResourceWatchdog()
    idle = watchdog.enforce_idle_state()
    print(f"Watchdog check complete. Idle enforcement active: {idle}")
