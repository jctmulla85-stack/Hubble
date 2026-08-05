import os
import time
from alpaca.trading.client import TradingClient
from alpaca.common.exceptions import APIError
from supervisor_v2 import AdvancedSupervisor

class ExecutionCore:
    def __init__(self):
        self.api_key = os.getenv("ALPACA_KEY_APEX_001")
        self.api_secret = os.getenv("ALPACA_SECRET_APEX_001")
        self.client = TradingClient(self.api_key, self.api_secret)
        self.supervisor = AdvancedSupervisor()
        self.paper = True

    def execute_signal(self, symbol, qty, side, signal_price):
        try:
            system_checks = self.supervisor.run_comprehensive_system_check()
            
            for component, status_dict in system_checks.items():
                if status_dict.get("status") == "ERROR":
                    print(f"ABORT: Execution halted by supervisor tier -> {component}")
                    return False

            print(f"GATEKEEPER PASSED: Routing {side.upper()} order for {qty} shares of {symbol}...")
            return True
            
        except APIError as e:
            print(f"ALPACA API ERROR during execution: {e}")
            return False
        except Exception as e:
            print(f"CRITICAL ERROR in execution core: {e}")
            return False

if __name__ == "__main__":
    core = ExecutionCore()
    print(f"Execution Core initialized and ready for live signals. (Paper Mode: {core.paper})")
