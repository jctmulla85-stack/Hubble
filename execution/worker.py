import time
import argparse
import logging
from execution.engine import Engine
from execution.backend import LiveAlpacaBackend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Worker")

class GovernorGuard:
    def __init__(self, live_backend, max_daily_drawdown_pct=0.05):
        self.live_backend = live_backend
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.starting_equity = None

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

        if self.starting_equity is None:
            self.starting_equity = current_equity
            return "APPROVE"

        if self.starting_equity > 0:
            drawdown = (self.starting_equity - current_equity) / self.starting_equity
            if drawdown >= self.max_daily_drawdown_pct:
                logger.error("[GovernorGuard] Max daily drawdown threshold breached.")
                return "VETOED"

        return "APPROVE"

def emit_heartbeat(worker_id):
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    args = parser.parse_args()

    print(f"[Worker] Initialized worker for account: {args.id}")
    
    import os
    api_key = os.getenv(f"ALPACA_KEY_{args.id}")
    api_secret = os.getenv(f"ALPACA_SECRET_{args.id}")
    
    api_client = None
    if api_key and api_secret:
        from alpaca.trading.client import TradingClient
        api_client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)

    backend = LiveAlpacaBackend(api_client=api_client) if api_client else None
    engine = Engine(api_client=backend)
    guard = GovernorGuard(live_backend=backend)

    while True:
        try:
            status = guard.evaluate()
            if status == "VETOED":
                print("[Worker] Execution vetoed by governor guard.")
            else:
                if engine and hasattr(engine, "run_tick"):
                    engine.run_tick()
                emit_heartbeat(args.id)
        except Exception as e:
            print(f"[Error] Execution loop failed: {e}")

        time.sleep(1)

if __name__ == "__main__":
    main()
