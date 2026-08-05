code = """import sys

class InstitutionalDefenseEngine:
    def __init__(self, trading_client, max_drawdown_pct=1.5, min_cash_threshold=0.0):
        self.client = trading_client
        self.max_drawdown_pct = max_drawdown_pct
        self.min_cash_threshold = min_cash_threshold
        self.starting_equity = None

    def initialize_session(self):
        account = self.client.get_account()
        self.starting_equity = float(account.equity)
        print(f"[DEFENSE ENGINE] Initialized. Baseline Equity: ${self.starting_equity:,.2f}")

    def check_circuit_breakers(self):
        account = self.client.get_account()
        current_equity = float(account.equity)
        current_cash = float(account.cash)
        drawdown_pct = ((self.starting_equity - current_equity) / self.starting_equity) * 100
        print(f"[DEFENSE] Equity: ${current_equity:,.2f} | Cash: ${current_cash:,.2f} | Drawdown: {drawdown_pct:.2f}%")
        if drawdown_pct >= self.max_drawdown_pct:
            print(f"[CRITICAL ALERT] Drawdown limit reached ({drawdown_pct:.2f}%). Flattening.")
            self.emergency_flatten()
            return False
        if current_cash < self.min_cash_threshold:
            print(f"[WARNING] Negative cash / margin drag detected (${current_cash:,.2f}).")
            return "HALT_NEW_ENTRIES"
        return "NORMAL"

    def validate_liquidity(self, symbol, bid, ask, volume):
        if ask <= 0 or bid <= 0:
            return False
        spread_pct = (ask - bid) / ask
        if spread_pct > 0.01 or volume < 1000:
            return False
        return True

    def emergency_flatten(self):
        try:
            self.client.close_all_positions(cancel_orders=True)
            print("[DEFENSE ENGINE] Positions flattened.")
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
"""

with open("institutional_defense.py", "w") as f:
    f.write(code)
print("[SUCCESS] institutional_defense.py generated successfully.")
