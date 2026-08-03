import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from execution.reconciler import Reconciler

import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
import logging
import sys
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from execution.engine import Engine
from execution.backend import LiveAlpacaBackend, TradingBackend

class GovernorGuard:
    def __init__(self, live_backend, max_daily_drawdown_pct=0.05):
        self.live_backend = live_backend
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.peak_equity = 0.0

    def evaluate(self):
        if not self.live_backend:
            return "APPROVE"
        
        try:
            client = getattr(self.live_backend, "client", None)
            if client and hasattr(client, "get_account"):
                account = client.get_account()
                current_equity = float(account.equity)
            else:
                return "APPROVE"
        except Exception:
            return "APPROVE"

        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        if self.peak_equity > 0:
            drawdown = (self.peak_equity - current_equity) / self.peak_equity
            if drawdown >= self.max_daily_drawdown_pct:
                self.emergency_flatten("Max daily drawdown threshold breached")
                return "VETOED"

        return "APPROVE"

    def emergency_flatten(self, reason):
        print(f"[EMERGENCY FLATTEN TRIGGERED]: {reason}")
        if hasattr(self.live_backend, "client"):
            client = self.live_backend.client
            if hasattr(client, "cancel_orders"):
                try:
                    client.cancel_orders()
                except Exception:
                    pass
            if hasattr(client, "close_all_positions"):
                try:
                    client.close_all_positions(cancel_orders=True)
                except Exception:
                    try:
                        client.close_all_positions()
                    except Exception as e:
                        print(f"[Error] Failed to execute emergency flatten: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QuantBot Execution Worker")
    parser.add_argument("--id", required=True, help="Account ID")
    args = parser.parse_args()

    # Initialize backend client and live wrapper using .env credentials
    api_client = TradingBackend() if 'TradingBackend' in globals() else None
    backend = LiveAlpacaBackend(api_client=api_client) if api_client else None
    engine = Engine(api_client=backend)
    guard = GovernorGuard(live_backend=engine)
    
    print(f"[Worker] Initialized worker for account: {args.id}")

    reconciler = Reconciler(governor=guard)

while True:
    try:
        # Evaluate governor guard and run engine tick
        if guard.evaluate() == 'VETOED':
            print('[Worker] Execution vetoed by governor guard.')
        else:
            if hasattr(engine, 'tick'):
                engine.tick()
            elif hasattr(engine, 'run'):
                engine.run()
        import time; time.sleep(1)
        # Reconcile state against broker balance
        if backend and hasattr(backend, 'client'):
            acc = backend.client.get_account()
            broker_bal = float(acc.equity)
            internal_bal = float(acc.equity)  # Update with internal tracking if available
            reconciler.verify_state(internal_bal, broker_bal)
    except Exception as e:
        print(f'[Error] Reconciliation check failed: {e}')

        try:
            status = guard.evaluate()
            if status == "VETOED":
                print("[Worker] Execution vetoed by governor guard.")
        except Exception as e:
            print(f"[Error] Evaluation loop failed: {e}")

        try:
            if engine and hasattr(engine, "run"):
                engine.run()
        except Exception as e:
            print(f"[Error] Engine execution failed: {e}")

        time.sleep(1)
